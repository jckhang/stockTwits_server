from yahoo_finance import Share
from flask import json
from flask import Flask
from datetime import datetime
from bson import json_util
from pipelines import MONGODBPipeline

db = MONGODBPipeline()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# if db.info_collection.count()==0:
#     with open('static/sp100.json', 'rb') as f:
#         ls = json.load(f)
#         for i in ls:
#             symbol = Share(i['name'])
#             i['price'] = symbol.get_price()
#             i['time'] = timestamp
#     result = db.info_collection.insert_many(ls)
#     # print ls
#     print result
l = list(db.info_collection.find({'sector':'Technology'}))


# print json.dumps(l, default=json_util.default)