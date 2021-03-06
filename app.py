from __future__ import print_function
from flask import Flask, render_template, request, json, jsonify, Response
from flask.ext.cors import CORS, cross_origin
from datetime import datetime
from yahoo_finance import Share
import unirest
import pytz
from misc.settings import ACCESS_TOKEN, MONGODBPipeline
import misc.stock_processing as ms
import pymongo
from stop_words import get_stop_words
from collections import Counter, OrderedDict
# App config
app = Flask(__name__)
app.config.from_object(__name__)
# Cors Config
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# Create Database Stock
db = MONGODBPipeline()
# Stopwords
stopW = set(get_stop_words('english'))
stopW.update(['will', 'can', 'just', 'www', 'com'])

# -------- Route to Manipulate Collection Infos --------
# API CIC(Collection Infos Create)


@app.route('/cic')
def createInfos():
    if db.infos.count() == 0:
        print("Creating Infos!!")
        with open('static/sp100.json', 'rb') as f:
            ls = json.load(f)
            for i in ls:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                symbol = Share(i['name'])
                item = {
                    'name': i['name'],
                    'price': symbol.get_price(),
                    'time': timestamp,
                    'prev_close': symbol.get_prev_close(),
                    'open': symbol.get_open(),
                    'volume': symbol.get_volume(),
                    'pe': symbol.get_price_earnings_ratio(),
                    'eps': symbol.get_earnings_share(),
                    'price_sales': symbol.get_price_sales(),
                    'ebitda': symbol.get_ebitda(),
                    'hotness': ms.hotness_function(i['name']),
                    'BS': ms.bs_function(i['name'])}
                db.infos.insert_one({
                    "name": i['name'],
                    "sector": i['sector'],
                    "data": [item]
                })
        print('Collection Infos Created.')
        return Response('Collection Infos Created.')
# createInfos()
# API CIU(Collection Iinfo Update)


@app.route('/ciu')
def updateInfos():
    print("Updating Infos!")
    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        for i in ls:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print (i['name'])
            symbol = Share(i['name'])
            item = {
                'name': i['name'],
                'price': symbol.get_price(),
                'time': timestamp,
                'prev_close': symbol.get_prev_close(),
                'open': symbol.get_open(),
                'volume': symbol.get_volume(),
                'pe': symbol.get_price_earnings_ratio(),
                'eps': symbol.get_earnings_share(),
                'price_sales': symbol.get_price_sales(),
                'ebitda': symbol.get_ebitda(),
                'hotness': ms.hotness_function(i['name']),
                'BS': ms.bs_function(i['name'])}
            db.infos.update(
                {"name": i['name']},
                {
                    "$push": {"data": item}
                }
            )
    print('Collection Infos Updated.')
    return Response('Collection Infos Updated.')
# API CID(Collection Infos Delete)


@app.route("/cid")
def deleteInfos():
    date = datetime.now()
    start = date.replace(hour=9, minute=0).strftime("%Y-%m-%d %H:%M:%S")

    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        for i in ls:
            data = filter(lambda x: x['time'] > start, [
                          j for i in db.infos.find({'name': i['name']}) for j in i['data']])
            db.infos.update_one({'name': i['name']}, {
                '$set': {
                    'data': data
                }
            }, upsert=False)
    return Response('Collection Infos Deleted.')

# --------- Route to Manipulate Collection Twits ----------
# API CTC(Collection Twits Create)


@app.route('/ctc')
def createTwits():
    def bs(record):
        if record is None:
            return 0
        else:
            return 1 if record['basic'] == "Bullish" else -1
    if db.twits.count() == 0:
        with open('static/sp100.json', 'rb') as f:
            ls = json.load(f)
            url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json?access_token={}"
            for i in ls:
                unirest.timeout(200)
                response = unirest.get(url.format(
                    i['name'], ACCESS_TOKEN))
                data = response.body
                msgs = data['messages']
                # print("Creating", i['name'], '....')
                # print(db.twits.count())
                for msg in msgs:
                    time = datetime.strptime(
                        msg['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    utc = pytz.utc
                    item = {
                        'name': msg['user']['username'],
                        'body': msg['body'],
                        'id': msg['id'],
                        'time': utc.localize(time).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                        'symbols': [i['symbol'] for i in msg['symbols']],
                        'reshares': msg['reshares']['reshared_count'],
                        'bs': bs(msg['entities']['sentiment'])}
                    try:
                        db.twits.replace_one(item, item, True)
                    except pymongo.errors.DuplicateKeyError:
                        pass
        print('Collection Twits Created.')
        return Response('Collection Twits Created.')
    return Response('Error Occurs.')

# createTwits()
# API CTU(Collection Twits Update)


@app.route('/ctu')
def updateTwits():
    def bs(record):
        if record is None:
            return 0
        else:
            return 1 if record['basic'] == "Bullish" else -1
    print("Updating Twits!!")
    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json?access_token={}"
        for i in ls:
            unirest.timeout(200)
            response = unirest.get(url.format(
                i['name'], ACCESS_TOKEN))
            data = response.body
            msgs = data['messages']
            # print("Updating", i['name'])
            # print(db.twits.count())
            for msg in msgs:
                time = datetime.strptime(
                    msg['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                utc = pytz.utc
                item = {
                    'name': msg['user']['username'],
                    'body': msg['body'],
                    'id': msg['id'],
                    'time': utc.localize(time).astimezone(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S'),
                    'symbols': [i['symbol'] for i in msg['symbols']],
                    'reshares': msg['reshares']['reshared_count'],
                    'bs': bs(msg['entities']['sentiment'])}
                try:
                    db.twits.replace_one(item, item, True)
                except pymongo.errors.DuplicateKeyError:
                    pass

    print('Collection Twits Update.')
    return Response('Collection Twits Updated.')
# API CTD(Collection Twits Delete)


@app.route("/ctd")
def deleteTwits():
    date = datetime.now()
    start = date.replace(hour=0, minute=0).strftime("%Y-%m-%d %H:%M:%S")
    db.twits.remove({"time":
                     {"$lt": start}
                     })
    print('Collection Twits Deleted.')
    return Response('Collection Twits Deleted.')
# API CKC(Collection Keywords Create)


@app.route("/ckc")
def createKeywords():
    if db.keywords.count() == 0:
        print("Creating Keywords!!")
        with open('static/sp100.json', 'rb') as f:
            ls = json.load(f)
            for i in ls:
                if i['name'] == "BRKB":
                    symbol = "BRK.B"
                else:
                    symbol = i['name']
                twits = [ms.regex(i['body']) for i in db.twits.find(
                    {"symbols": {"$elemMatch": {"$eq": symbol}}}, projection={"_id": 0, "id": 0, "reshares": 0})]
                words = reduce(lambda x, y: x + y, twits)
                clean_words = Counter()
                for key, value in words.iteritems():
                    if not key.lower() in stopW and key.isalpha() and len(key) >= 2:
                        clean_words[key[0].upper() + key[1:]] = value
                item = {'name': symbol, 'data': OrderedDict(
                    clean_words.most_common(25))}
                try:
                    db.keywords.replace_one(item, item, True)
                except pymongo.errors.DuplicateKeyError:
                    pass
    print('Collection Keywords Created.')
    return Response('Collection Keywords Created.')
# API CKU(Collection Keywords Update)


@app.route("/cku")
def updateKeywords():
    print("Updating Keywords!!")
    with open("static/sp100.json", "rb") as f:
        ls = json.load(f)
        for i in ls:
            if i['name'] == "BRKB":
                symbol = "BRK.B"
            else:
                symbol = i['name']
            twits = [ms.regex(i['body']) for i in db.twits.find(
                {"symbols": {"$elemMatch": {"$eq": symbol}}}, projection={"_id": 0, "id": 0, "reshares": 0})]
            words = reduce(lambda x, y: x + y, twits)
            clean_words = Counter()
            for key, value in words.iteritems():
                if not key.lower() in stopW and key.isalpha() and len(key) >= 2:
                    clean_words[key[0].upper() + key[1:]] = value
            item = {'name': symbol, 'data': OrderedDict(
                clean_words.most_common(25))}
            try:
                db.keywords.replace_one(item, item, True)
            except pymongo.errors.DuplicateKeyError:
                pass
    print("Collection Keywords Updated.")
    return Response("Collection Keywords Updated.")
# API CKD(Collection Keywords Delete)


@app.route("/ckd")
def deleteKeywords():
    db.keywords.delete_many({})
    print('Collection Keywords Deleted.')
    return Response('Collection Keywords Deleted.')
# ===============Route for API GET===============
# Route for homepage


@app.route("/")
def home():
    return render_template("home.html", name="home")
# Route for getting symbol within sector


@app.route("/sectors", methods=["GET"])
@cross_origin()
def sectionAPI():
    if not('sector' in request.args) or (request.args['sector'] == 'all'):
        sector = "S&P 100 Index Symbols"
        data = [i['data'][len(i['data']) - 1]
                for i in db.infos.find()]
        return jsonify({sector: data})

    else:
        sector = request.args['sector'][
            0].upper() + request.args['sector'][1:] + " Sector Symbols"
        data = [i['data'][len(i['data']) - 1]
                for i in db.infos.find({'sector': request.args['sector']})]
        return jsonify({sector: data})
# Route for searching specific symbol and it's general information


@app.route("/search", methods=["GET"])
@cross_origin()
def searchAPI():
    name = request.args['symbol']
    data = [j
            for i in db.infos.find({'name': name}) for j in i['data'][-30:]]
    return jsonify({'data': data})
# Route for searching specific symbol and return it's first 30 twits


@app.route("/twits", methods=["GET"])
@cross_origin()
def twitsAPI():
    if not('symbol' in request.args) or (request.args['symbol'] == 'all'):
        data = [i for i in db.twits.find(
            {}, projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(50)]
        return jsonify({'data': data})
    else:
        name = request.args['symbol']
        data = [i for i in db.twits.find(
            {"symbols": {"$elemMatch": {"$eq": name}}},
            projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(50)]
    return jsonify({'data': data})
# Route for searching specific symbol and return it's most common 25 keywords.


@app.route('/keywords', methods=["GET"])
@cross_origin()
def keywordsAPI():
    name = request.args['symbol']
    data = [i['data'] for i in db.keywords.find({'name': name})]
    return jsonify({'data': data})
# Route for realted stocks


@app.route('/related', methods=["GET"])
@cross_origin()
def related():
    symbol = request.args['symbol']
    data = [i for i in db.twits.find({'symbols': {"elemMatch": {"$eq": symbol}}})]
    return jsonify({'data': data})
# Route for listing the price of each stocks in the past 24 hours.


@app.route('/sparkline', methods=["GET"])
@cross_origin()
def sparkline():
    name = request.args['symbol']
    price = [j['price']
             for i in db.infos.find({'name': name}) for j in i['data']]
    bs = [j['BS']
          for i in db.infos.find({'name': name}) for j in i['data']]
    time = [j['time']
            for i in db.infos.find({'name': name}) for j in i['data']]
    return jsonify({'price': price,
                    'BS': bs,
                    'time': time,
                    'start': time[0][11:13] + ':00',
                    'end': time[-1][11:13] + ':00'})
# Error Handler


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    return jsonify(message)

# # # Testing

# # : Route for testing hotness function
#
#
# @app.route("/hot", methods=['GET'])
# @cross_origin()
# def hot():
#     symbol = request.args['symbol']
#     hotness = ms.hotness_function(symbol)
#     return jsonify({('{} hotness'.format(symbol)): hotness})
# # Route for testing bs function
#
#
# @app.route("/bs", methods=['GET'])
# @cross_origin()
# def bs():
#     symbol = request.args['symbol']
#     bs = ms.bs_function(symbol)
#     return jsonify({('{} bs'.format(symbol)): bs})
# Route for getting price for specific symbol.

if __name__ == "__main__":
    app.run(debug=True)
