from pymongo import MongoClient
import os
import requests
import json
from dotenv import load_dotenv
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

# import of Paris districts' collection, (with feature!!!)
with open('feature.geojson') as geo_file:
    geo_feature = json.load(geo_file)

def arrondissement_scraping ():
    '''
    Function that scraps a table from wikipedia containing info for Paris' districts.
    Does not take any argument and returns a dataframe with the name of each district sorted alphabetically and its area.
    '''

    url = 'https://en.wikipedia.org/wiki/Arrondissements_of_Paris'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    table = soup.find_all("table", attrs = {"class":"wikitable"})
    arrondissements_info = pd.read_html(table[0].prettify())[0]
    arrondissements_info['Area (km  2  )'] = arrondissements_info['Area (km  2  )'].apply(lambda x: x.split('km')[0])
    arrondissements_info['Area (km  2  )'] = arrondissements_info['Area (km  2  )'].apply(lambda x: x.split('\xa0')[0])
    arrondissements_info['Area (km  2  )'] = arrondissements_info['Area (km  2  )'].apply(lambda x: float(x))
    districts_area = arrondissements_info[['Name', 'Area (km  2  )']]
    districts_area.rename(columns={'Area (km  2  )': 'Area'}, inplace = True, errors = 'raise')

    # Since first 4 districts are grouped together in area and they have similar shape:
    for i in range(4):
        districts_area.loc[i, 'Area'] = (districts_area.iloc[i]['Area']/4)

    districts_area.sort_values(by = ['Name'], ascending = True, inplace = True)
    districts_area.reset_index(drop = True, inplace = True)

    return districts_area

# Dataframe with each district area in squared kilometers.
area_info = arrondissement_scraping()

def foursquare_query (query, category, place, limit=10):
    '''
    Function that makes 4square queries
    It takes the query, e.g. Starbucks, Airports, Dog hairdressers, etc., the reference point (Paris), and a 
    limit of results.
    Returns a single-column dataframe with shapely Points, the coordinates of each establishment or instance.
    '''
    # url for the API query
    url = f"https://api.foursquare.com/v3/places/search?query={query}&categories={category}&near={place}&sort=DISTANCE&limit={limit}"

    headers = {
        "accept": "application/json",
        "Authorization": foursquare_key
    }

    # full response
    response = requests.get(url, headers=headers).json()['results']
    # name of the establishment
    response[0]['name']
    # coordinates
    response[0]['geocodes']['main']['latitude']
    response[0]['geocodes']['main']['longitude']

    # we append Point tupples with lon, lat coordinates to the request_points list:
    request_points = []
    for i in range(len(response)):
        request_points.append(Point(response[i]['geocodes']['main']['longitude'], response[i]['geocodes']['main']['latitude']))
    name_list = [response[i]['name'] for i in range(len(response))]

    # creation of dataframe with the actual shapely Point coordinates
    d = {'Coordinates': request_points, 'Name': name_list, 'Type': response[i]['categories'][0]['name']}
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

    with open('feature.geojson') as geo_file:
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
    count_df.rename(columns={'index': 'District', 0: 'Density'}, inplace=True, errors='raise')
    count_df.sort_values(by = ['District'], ascending = True, inplace = True)
    count_df.reset_index(inplace = True, drop = True)

    # weighted count by district area: 
    for i in range(count_df.shape[0]):
        count_df.loc[i, 'Density'] = count_df.loc[i, 'Density'] / area_info.iloc[i]['Area']

    return count_df

# Feature geojson is the one used to plot (ALSO USEFUL TO PLOT PUNCTUATIONS)
def district_distribution (count_df):
    '''
    Function that plots the establishments distribution in Paris' districts.
    Takes the count dataframe obtained in the function above, with the count of establishments per district
    Returns the map plot of this distribution.
    '''
    paris_map = Map(location = [48.86, 2.35], zoom_start = 9)
    folium.Choropleth(
        geo_data=geo_feature,
        data=count_df,
        columns=count_df.columns,
        key_on="feature.properties.name",
    ).add_to(paris_map)
    
    return paris_map

def distance_criteria (query, category):
    '''
    Function defined to run into distance criteria function, running specific queries at 4 square to get distances from
    each district to the place queried.
    It takes the query as argument
    Returns a dataframe with the distances ordered and the attribution of points according to the ponderation system.
    '''

    # created a dict that stores the center point of each district, to take it as reference for distances
    district_centre_dict = {}
    for feature in geo_feature['features']:
        polygon = shape(feature['geometry'])
        district_centre_dict[feature['properties']['name']] = (polygon.centroid.y,polygon.centroid.x)

    # dict to store distances from district center to closest queried place
    distance_from_centre = {}

    # url for the API query
    for district, centre_point in district_centre_dict.items():
        url = f"https://api.foursquare.com/v3/places/search?query={query}&categories={category}&ll={centre_point[0]}%2C{centre_point[1]}&sort=DISTANCE&limit=1"

        headers = {
            "accept": "application/json",
            "Authorization": foursquare_key
        }
        # full response
        dist_resp = requests.get(url, headers=headers).json()['results'][0]['distance']

        # we get the distance of first response since we sort by distance and the criteria here is to get closest queried items.
        distance_from_centre[district] = dist_resp

    distance_from_centre = pd.DataFrame.from_dict(distance_from_centre, orient='index').reset_index(drop=False)
    distance_from_centre.rename(columns = {'index': 'District', 0: 'Distance'}, inplace = True, errors = 'raise')
    distance_from_centre.sort_values(by = ['District'], ascending = True, inplace = True)
    distance_from_centre.reset_index(drop=True, inplace = True)

    return distance_from_centre