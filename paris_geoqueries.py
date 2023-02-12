from pymongo import MongoClient
import os
import requests
import json
from dotenv import load_dotenv
from bson.json_util import dumps
import pandas as pd
import folium
from folium import Choropleth, Circle, Marker, Icon, Map, TileLayer
from bs4 import BeautifulSoup
import shapely
from shapely import Polygon
from shapely.geometry import shape, Point

# we import the 4square key from the .env file to make geoqueries.
load_dotenv()
foursquare_key = os.getenv('fsq_key')

# import of Paris collection from MongoDB, useful to get the list of districts (without feature!!!)
client = MongoClient('localhost:27017')
db = client.get_database('ironhack')
paris = db.get_collection('paris')
paris = list(paris.find())


def foursquare_query (query, place, limit=10):
    '''
    Function that makes 4square queries
    It takes the query, e.g. Starbucks, Airports, Dog hairdressers, etc., the reference point (Paris), and a 
    limit of results.
    Returns a single-column dataframe with shapely Points, the coordinates of each establishment or instance.
    '''
    # url for the API query
    url = f"https://api.foursquare.com/v3/places/search?query={query}&near={place}&limit={limit}"

    headers = {
        "accept": "application/json",
        "Authorization": foursquare_key
    }

    # full response
    response = requests.get(url, headers=headers).json()['results']

    # we append Point tupples with lon, lat coordinates to the request_points list:
    request_points = []
    for i in range(len(response)):
        request_points.append(Point(response[i]['geocodes']['main']['longitude'], response[i]['geocodes']['main']['latitude']))

    # creation of dataframe with the actual shapely Point coordinates
    d = {response[0]['categories'][0]['name']: request_points, 'Name': response[i]['name']}
    df = pd.DataFrame(data=d)
    return df

def spot_finder (df):
    '''
    Function that counts instances per district in Paris.
    Takes the dataframe obtained in the 4 square geoquery
    Returns a dictionary with the count of establishments per district.
    '''

    # We append the list of districts as keys in a dict, and set a default value of 0 for each key.
    district_list = [paris[i]['properties']['name'] for i in range(len(paris))]
    dict_count = {}
    for i in district_list:
        dict_count[i] = 0

    with open('feature.geojson') as geo_file: # In this one, paris geojson including feature!!!
        geo_feature = json.load(geo_file)

    # Iteration through each pair of coordinates to see what Paris district they match, being districts defined in geo_feature file.
    for establishment in df['Coordinates']:
        for feature in geo_feature['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(establishment):
                # Addition to the correspondent district in case the coordinate matches.
                if feature["properties"]["name"] in dict_count:
                    dict_count[feature["properties"]["name"]] += 1

    count_df = pd.DataFrame.from_dict(dict_count, orient="index").reset_index(drop=False)
    count_df.rename(columns={'index': 'District', 0: 'Count'}, inplace=True, errors='raise')

    return count_df

def map_distribution_plot (count_df):
    