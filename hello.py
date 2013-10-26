import os
import urlparse
import json
import re

import requests

from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)

from pyechonest import config, artist
config.ECHO_NEST_API_KEY = 'WOUHTN44BMS5SMPF2'

import redis
url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)

from names import male_names, female_names
males_names_list = male_names()
female_names_list = female_names()

def pronoun_search(the_artist):
    bios = []
    word_count = 0
    male_pronoun_count = 0
    female_pronoun_count = 0
    male_name_count = 0
    female_name_count = 0

    bio_data = the_artist.biographies
    for bio in bio_data:
        bios.append(bio['text'])

    for bio in bios:
        bio_list = bio.split(' ')
        word_count = word_count + len(bio_list)
        bio_list = [word.strip(',./`!@#$%^&*()-_=+|\][{}') for word in bio_list]
        
        pronouns = {'he': 0,
                    'she': 0,
                    'him': 0,
                    'her': 0,
                    'his': 0,
                    'hers': 0,
                    'himself': 0,
                    'herself': 0,
         }
        
        for pronoun in pronouns:
            pronouns[pronoun] = bio_list.count(pronoun)
        male_pronoun_count = male_pronoun_count + pronouns['he'] + pronouns['him'] + pronouns['his'] + pronouns['himself']
        female_pronoun_count = female_pronoun_count + pronouns['she'] + pronouns['her'] + pronouns['hers'] + pronouns['herself']

        for name in male_names(): 
             male_name_count = male_name_count + bio_list.count(name)
        for name in female_names(): 
             female_name_count = female_name_count + bio_list.count(name)
    return {'number_bios': len(bios), 'male_pronouns': male_pronoun_count, 'female_pronouns': female_pronoun_count, 
                'male_names': male_name_count, 'female_name_count': female_name_count, 'word_count': word_count}

def _clean_tags(string):
    string = string.replace('<td>', '')
    string = string.replace('</td>', '')
    string = string.replace('<br />', '')
    string = string.replace('</a>', '')
    if '<a href' in string:
        string = re.search(r'<a href=.+?>(.+)', string, re.S).group(1)
    return string.strip()

def wiki_member_search(the_artist):
    if the_artist.urls.get('wikipedia_url', None):
        wiki_url = the_artist.urls['wikipedia_url']

        print "IN WIKI SEARCH:  %s" % wiki_url

        res = requests.get(wiki_url)
        print "made it past the requests request"

        body = res.text
        infobox = re.search(r'<table class="infobox.+?</table>', body, re.S).group()
        print "made it past the first big regex"


        if 'Members' not in infobox:
            print "members not found"
            number_members = 1
            men = 0
            women = 0
            members = ''
        else:
            print "members found"
            men = 0
            women = 0
            members = re.search(r'<th scope="row" style="text-align:left;">Members</th>(.+?)</tr>', infobox, re.S).group(1)
            print "made it past second big regex"
            members = members.split('<br />')
            members = [_clean_tags(m) for m in members]
            number_members = len(members)
            for name in members:
                if ' ' in name:
                    if name.split(' ')[0] in males_names_list:
                        men = men + 1
                    elif name.split(' ')[0] in females_names_list:
                        women = women + 1
                else:
                    if name in males_names_list:
                        men = men + 1
                    elif name in females_names_list:
                        women = women + 1

        print "men:  %d -- women:  %d" % (men, women)
        return {'wiki_url': wiki_url, 'members': number_members, 'men': men, 'women': women, 'member_names': members}
    else:
        return {'wiki_url': ''}
        

def discogs_release_search(the_artist):
    discogs_id = the_artist.get_foreign_id('discogs').split(':')[2]
    url = 'http://api.discogs.com/artists/%s/releases' % discogs_id
    r = requests.get(url)
    print "DISCOGS:  made it past the requests request"

    releases = []
    # Discogs data is terrible.  Fuck. We'll use this as a row of thumbnails and links below the Rdio player
    # CLOSE ENOUGH FOR SEISMOLOGY
    for release in r.json().get('releases', [])[0:10]:
        releases.append({'title': release.get('title', ''), 'thumbnail': release.get('thumb', ''), 'url': release.get('uri', '')})
    return releases

def find_artist_data(artist_name):

    the_artist = artist.search(artist_name, results=1)[0]

    print "the artist we found %s" % the_artist
    if not the_artist:  
        return ''

    data = {}
    data['artist'] = the_artist.name

    pronouns_dict = pronoun_search(the_artist)
    data.update(pronouns_dict)
    print "we got the pronoun dict"

    wiki_dict = wiki_member_search(the_artist)
    data.update(wiki_dict)
    print "we got the wiki dict"

    images = the_artist.images
    data['image_urls'] = [image['url'] for image in images[0:5]]
    print "we got the echonest images"

    data['discogs_release'] = discogs_release_search(the_artist)
    print "we got the discogs releases"

    print "in find_artist_data, with a dict of %s" % data

    # number of bios, number of words, members, gender of members, number of male pronouns, number of female pronouns
    # number of male names, number of female names
    # echonest image - 5
    # discogs releases, discogs images, discogs links


    # TODOS:
    # Data for Tom Waits, CHVRCHES, My Bloody Valentine
    # - Make the front end
    # - Scrape Discogs properly
    # - Get sound from Rdio
    # then I need to run this on ~5,000 hottt artists
    # then I need to make the front end.  Gotta get up early early tomorrow

    # and that includes making our guess.  Solo artists, we use pronouns.  Multi artists, we use name match on membmers, weighted by pronouns


    
    return json.dumps(data)



@app.route('/', methods=['GET'])
def hello():
    return "feminest server 1.0"

@app.route('/get-data/<artist_name>', methods=['GET'])
def get_data(artist_name):
    '''Get the logged data for a given artist name''' 
    res_string = redis.get(artist_name)
    res_dict = json.loads(res_string)
    return jsonify(**res_dict)


@app.route('/find-data/<artist_name>', methods=['GET'])
def find_data(artist_name):
    '''Find data and write data for a given artist name'''

    # Do the work.
    print "in find-data, just before the call"
    artist_json = find_artist_data(artist_name)
    print "the json %s" % artist_json

    # Write to redis - careful of json formatting - this needs to be a string.  
    redis.set(artist_name, artist_json)
    return "feminest::find %s" % (artist_name)