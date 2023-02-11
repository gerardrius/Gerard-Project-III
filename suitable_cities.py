import pandas as pd
import json

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