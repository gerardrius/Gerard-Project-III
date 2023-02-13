from sklearn import preprocessing
import pandas as pd

def density_or_points_normalizer (df, query):
    values_array = df['Density'].values #returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    values_array = values_array.reshape(-1,1)
    scaled_values = min_max_scaler.fit_transform(values_array)
    new_column = pd.DataFrame(scaled_values)
    new_column.rename(columns = {0: query}, inplace = True, errors = 'raise')
    return new_column