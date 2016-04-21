# from yahoo_finance import Share
# from flask import json
# from datetime import datetime
from pipelines import MONGODBPipeline

db = MONGODBPipeline()
# timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# if db.info_collection.count() == 0:
#     with open('static/sp100.json', 'rb') as f:
#         ls = json.load(f)
#         for i in ls:
#             symbol = Share(i['name'])
#             i['price'] = symbol.get_price()
#             i['time'] = timestamp
#     result = db.info_collection.insert_many(ls)
# print db.info_collection.count()
a = db.twits_collection.find(
    {'name': 'AAPL'}, {'data': 1, '_id': 0}).sort([("data.id", -1)])
print a[0]['data'][0]['id']
