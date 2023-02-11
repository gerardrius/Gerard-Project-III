import pandas as pd
import json
import geopandas as gdp
from cartoframes.viz import Map, Layer, popup_element

def json_load (json_file):
  with open(json_file) as f:
    queried_db = json.load(f)
    return queried_db

def companies_distribution (json_file):
    '''
    Function that provides a dataframe with offices' geographical distribution.
    Takes the json file as argument and returns the dataframe with companies' name and their offices' geographic data. 
    '''
    # creation of lists to which append information of interest, through the iteration below.
    names_list = []
    city_list = []
    zip_list = []
    latitude_list = []
    longitude_list = [] 

    for company_index in range(len(json_file)):
        for office_index in range(len(json_file[company_index]['offices'])):
            names_list.append(json_file[company_index]['name'])
            city_list.append(json_file[company_index]['offices'][office_index]['city'])
            zip_list.append(json_file[company_index]['offices'][office_index]['zip_code'])
            latitude_list.append(json_file[company_index]['offices'][office_index]['latitude'])
            longitude_list.append(json_file[company_index]['offices'][office_index]['longitude'])

    # creation of the dictionary storing each list and conversion from dict to df
    data_dict = {
        'name': names_list,
        'city': city_list,
        'zip': zip_list,
        'lat': latitude_list,
        'lon': longitude_list
    }
    
    df = pd.DataFrame(data_dict)
    return df

def df_info (df):
    """
    Function that provides an overview of a dataframe's data and its quality
    Covers points such as cities and companies with the most offices and null values in geographical coordinates.
    """
    for column in df.columns:
        if column == 'name':
            name = df[column].value_counts().reset_index(drop = False)[:3]
            name.rename(columns={'index': 'company', 'name': 'count'}, inplace=True, errors='raise')
            print(f"The companies with most offices are {name['company'][0]}, {name['company'][1]} and {name['company'][2]}, with {name['count'][0]}, {name['count'][1]} and {name['count'][2]} offices respectively.")

        elif column == 'city':
            city = df[column].value_counts().reset_index(drop = False)[:3]
            city.rename(columns={'index': 'city', 'city': 'count'}, inplace=True, errors='raise')
            print(f"The cities with the most offices are {city['city'][0]}, {city['city'][1]} and {city['city'][2]}, with {city['count'][0]}, {city['count'][1]} and {city['count'][2]} offices respectively.")

        elif column == 'lat':
            print(f"The {(df[column].isna().sum())/(len(df['lat']))*100}% of latitude cells are empty.")
        elif column == 'lon':
            print(f"The {(df[column].isna().sum())/(len(df['lon']))*100}% of longitude cells are empty.")


def map_office_distribution (df):
    '''
    Funciton that provides a picture of the offices distribution accross the globe
    Takes the offices' distribution dataframe as argument and 
    returns a map with plotted geographic points where companies have their offices.
    '''
    gdf = gdp.GeoDataFrame(df, geometry=gdp.points_from_xy(df["lon"], df["lat"]))
    gdf = gdf.dropna(axis = 0,how = 'any')
    map = Map(Layer(gdf, "color:blue", popup_hover=[popup_element("name", "Office")]))

    print(f'The cities with the most offices are')
    return map

def city_count (df):
    '''
    Function that provides a numeric picture of the distribution of the map above.
    Takes the offices' distribution dataframe and
    returns a dataframe with the five highest counts of offices per city.
    '''
    cities_df = df['city'].value_counts()[:5].reset_index(drop=False)
    cities_df.rename(columns={'index': 'city', 'city': 'count'}, inplace=True, errors='raise')
    
    print(f"The most suitable cities are {cities_df['city'][0]} and {cities_df['city'][1]}, with {cities_df['count'][0]} and {cities_df['count'][1]} offices respectively")
    return cities_df