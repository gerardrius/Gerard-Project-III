# Import of all functions and libraries from the project.
from companies_collection import *
from suitable_cities import *
from paris_geoqueries import *
from ponderation import *

# COMPANIES COLLECTION (MONGO DB)
client = MongoClient('localhost:27017')
db = client.get_database('ironhack')
companies = db.get_collection('companies')

companies = mongo('ironhack', 'companies') # we get companies collection from mongo

collection_queried (companies) # asks what company categories to keep and money raised minimum, exports a json file (¡¡¡Remove last comma from it!!!)

# SUITABLE CITIES
queried_db = json_load('queried_db.json') # we import the json from previous query (REMOVE COMMA!)

offices_df = companies_distribution(queried_db) 

df_info(offices_df)

map_office_distribution(offices_df) # plotted coordinates of offices that fulfill query requirements.

city_count(offices_df) # city distribution of all offices (with/without coordinates).

# In this case, the suitable city turns out to be Paris. In case of different query results, get the correspondent geojson.


# PARIS GEOQUERIES
load_dotenv()
foursquare_key = os.getenv('fsq_key') # Foursquare key to get API queries.

client = MongoClient('localhost:27017') # Paris collection from geojson uploaded in MongoDB (without feature, meaning that Mongo has a collection for every district).
db = client.get_database('ironhack')
paris = db.get_collection('paris')
paris = list(paris.find())

with open('feature.geojson') as geo_file: # with feature, meaning that a single collection contains all districts!!!
    geo_feature = json.load(geo_file)

area_info = arrondissement_scraping() # Area of each Paris' district.

# Definition of most important functions (imported from paris_geoqueries):
    # Density functions
        # foursquare_query (query, category, place, limit=10)
        # spot_finder (df), the one returned from foursquare_query function

    # Distance functions
        # distance_criteria (query, category) a string and category code

    # Plot function
        # district_distribution (count_df) -> plots df with district and a single variable count in Paris map.

# PONDERATION
# Normalization function
    # density_or_points_normalizer (df, query)
    # explanation:  normalizes all values of distance or density between 0 and 1. In density, the higher it is, the closer to 1; in distance, the shortest, the closest to 1.
    #               The highest value will get a 1, the lowest a 0. Intermediate values are distributed within the proportion between original min and max.                


# We run all correspondent functions for each variable of interest

# Airports
airport_query = distance_criteria ('Airport', 19040)
airport_normalized = density_or_points_normalizer(airport_query, 'Airports')

# Dog hairdresser
dog_grooming_query = distance_criteria ('', 11134)
airport_normalized = density_or_points_normalizer(dog_grooming_query, 'Dog grooming')

# Basketball courts
basketball_query = distance_criteria ('Basket', 18008)
basketball_normalized = density_or_points_normalizer(basketball_query, 'Basket Court')

# Elementary schools
schools_query = foursquare_query('School', 12058, 'Paris', 50)
school_density = spot_finder(schools_query)
school_normalized = density_or_points_normalizer(school_density, 'Schools')

# Vegan restaurants
vegan_query = foursquare_query('Vegan', 13377, 'Paris', 50)
vegan_density = spot_finder(vegan_query)
vegan_normalized = density_or_points_normalizer(vegan_density, 'Vegan restaurants')

# Starbucks
starbucks_query = foursquare_query('Starbucks', 13035, 'Paris', 50)
starbucks_density = spot_finder(starbucks_query)
starbucks_normalized = density_or_points_normalizer(starbucks_density, 'Starbucks')

# Ratings per district
ponderation = ponderation_classification
print(ponderation)

# Paris map plot of ratings distribution!
print(district_distribution(ponderation))