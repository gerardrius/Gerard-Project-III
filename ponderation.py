from sklearn import preprocessing
import pandas as pd
from paris_geoqueries import *

def density_or_points_normalizer (df, query):
    '''
    Function that normalizes the scale of ponderation for each variable, giving them the same weight
    Takes the dataframe of each distance or density variable, together with the name of the queried item (which will be the returned column's name)
    Returns a single column df with the weighted ponderation.
    '''
    if 'Density' in df.columns:
        # density queried variables will give more points for higher density until no points for the lesser!
        values_array = df['Density'].values #returns a numpy array
        min_max_scaler = preprocessing.MinMaxScaler()
        values_array = values_array.reshape(-1,1)
        scaled_values = min_max_scaler.fit_transform(values_array)
        new_column = pd.DataFrame(scaled_values)
        new_column.rename(columns = {0: query}, inplace = True, errors = 'raise')
        area_info[query] = new_column
        return area_info
    
    elif 'Distance' in df.columns:
        # variables queried by distance will give more points for the shorter distances until no points for the longest! 
        df['Distance'] = df['Distance'].apply(lambda x: -x)
        values_array = df['Distance'].values #returns a numpy array
        min_max_scaler = preprocessing.MinMaxScaler()
        values_array = values_array.reshape(-1,1)
        scaled_values = min_max_scaler.fit_transform(values_array)
        new_column = pd.DataFrame(scaled_values)
        new_column.rename(columns = {0: query}, inplace = True, errors = 'raise')
        area_info[query] = new_column
        return area_info


def full_density_query (query, category, place, limit):
    query = foursquare_query(query, category, place, limit)
    density = spot_finder(query)
    normalization = density_or_points_normalizer(density, query)
    return normalization

def full_distance_query (query1, category):
    query = distance_criteria(query, category)
    normalization = density_or_points_normalizer(query, query1)
    return normalization

def ponderation_classification ():
    area_info.drop(['Area'], inplace=True, axis='columns')
    area_info['Sums'] = area_info.sum(axis=1)
    ponderation = area_info[['Name', 'Sums']]
    return ponderation