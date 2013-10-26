import os
import urlparse
import json
from flask import Flask
from flask import request
from flask import jsonify

from pyechonest import config, artist
config.ECHO_NEST_API_KEY = 'WOUHTN44BMS5SMPF2'

import redis
url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)

app = Flask(__name__)

def pronoun_search(the_artist):
    bios = []
    male_pronoun_count = 0
    female_pronoun_count = 0
    male_name_count = 0
    female_name_count = 0

    bio_data = the_artist.biographies
    for bio in bio_data:
        bios.append(bio['text'])

    for bio in bios:
        bio_list = bio.split(' ')
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
                'male_names': male_name_count, 'female_name_count', female_name_count)



def find_artist_data(artist_name):

    the_artist = artist.search(artist_name, results=1)[0]
    if not the_artist:  
        return ''

    pronouns_dict = pronoun_search(the_artist)

    data = {}
    data['artist'] = the_artist.name
    data.update(pronouns_dict)

    
    # number of bios, number of words, members, gender of members, number of male pronouns, number of female pronouns
    # number of male names, number of female names
    # our guess
    # echonest images
    # discogs releases, discogs images, discogs links

    
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
    artist_json = find_artist_data(artist_name)

    # Write to redis - careful of json formatting - this needs to be a string.  
    redis.set(artist_name, artist_json)
    return "feminest::find %s" % (artist_name)