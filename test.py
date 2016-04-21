# from yahoo_finance import Share
# from flask import json
# from datetime import datetime
from pipelines import MONGODBPipeline
from flask import json
import unirest
db = MONGODBPipeline()
# a = db.twits_collection.find(
#     {'name': 'AAPL'}, {'data': 1, '_id': 0}).sort([("data.id", -1)])
# print a[0]['data'][0]
# with open('static/sp100.json', 'rb') as f:
#     ls = json.load(f)
#     for i in ls:
#         response = unirest.get("https://api.stocktwits.com/api/2/streams/symbol/{0}.json".format(
#             i['name']))
#         data = response.body
#         msgs = data['messages']
#         item = {}
#         for msg in msgs:
#             item = {}
#             item['name'] = msg['user']['username']
#             item['body'] = msg['body']
#             item['id'] = msg['id']
#             item['time'] = msg['created_at']
#             a = db.twits_collection.find(
#                 {'name': i['name']},
#                 {'data': 1, '_id': 0}).sort([("data.id", -1)])
#             max_id = a[0]['data'][0]['id']
#             print i
#             if msg['id'] > max_id:
#                 db.twits_collection.update(
#                     {"name": i['name']},
#                     {
#                         "$push": {"data": item}
#                     }
#                 )
a = db.twits_collection.find(
    {'name': 'BK'}, {'data': 1, '_id': 0}).sort([("data.id", -1)])
print a[0]['data'][0]