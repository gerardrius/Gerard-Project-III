# Libraries
from pymongo import MongoClient
from bson.json_util import dumps
import pandas as pd

# Companies' collection
client = MongoClient('localhost:27017')
db = client.get_database('ironhack')
companies = db.get_collection('companies')

# Companies' collection with function
def mongo (database, collection):
    client = MongoClient('localhost:27017')
    db = client.get_database(database)
    c = db.get_collection(collection)
    return c

def collection_queried (collection, money, scale):
    '''
    Function that asks what business activities the company should compare to.
    Accepts the collection to query, the money amount and the scale of this amount (k/M).
    Exports the filtered collection directly.
    '''
    # First part: creates query for categories, based on the user interaction through inputs.
    categories_list = []
    cat_keeper = '--'
    for category in collection.distinct('category_code'):
        while len(cat_keeper) != 1 and cat_keeper not in ['Y', 'N']:
            cat_keeper = input(f"Do you want to keep {category} in the collection? (Y/N)")   
            if cat_keeper == 'Y':
                categories_list.append(category)
                cat_keeper = '--'
                break
            elif cat_keeper == 'N':
                cat_keeper = '--'
                break
            else:
                cat_keeper = '--'
    
    regex_expression = '(' +  "|".join(categories_list) + ')'
    query_category = {'category_code': {'$regex': regex_expression}}

    # Second part: query for total money raised.
    if scale == 'm' or scale == 'M':
        query_scale = {'total_money_raised': {'$regex': '(?i)m'}} # This query accepts M amounts and avoids K quantities.
        query_amount = {'total_money_raised': {'$gte': f'{money}M'}}
    elif scale == 'k' or scale == 'K':
        query_scale = {'total_money_raised': {'$regex': '(?i)k'}} # This query accepts M amounts and avoids K quantities.
        query_amount = {'total_money_raised': {'$gte': f'{money}k'}}
    
    # Third part: applying queries and export of the collection.
    total_query = {'$and': [query_amount, query_scale, query_category]}
    queried_db = list(companies.find(total_query))

    df = pd.DataFrame(queried_db)
    df.to_csv('companies_queried.csv', index=False)

    cursor = companies.find(total_query)
    with open('queried_db.json', 'w') as file:
        file.write('[')
        for document in cursor:
            file.write(dumps(document))
            file.write(',')
        file.write(']')
    
    return f'The collection has been exported, with a total remaining of {len(queried_db)} companies!'