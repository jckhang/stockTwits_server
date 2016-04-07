from yahoo_finance import Share
from flask import json
from datetime import datetime
from bson.json_util import dumps
from pipelines import MONGODBPipeline

db = MONGODBPipeline()
# if db.info_collection.count()==0:
#     with open('static/sp100.json', 'rb') as f:
#         ls = json.loads(json.load(f))
#         for i in ls:
#             symbol = Share(i['name'])
#     result = db.info_collection.insert_many(ls)
# timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# i['price'] = symbol.get_price()
# print timestamp

resp = dumps([i for i in db.info_collection.find({})])
print resp