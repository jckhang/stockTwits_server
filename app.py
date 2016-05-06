from flask import Flask, render_template, request, json, Response
from flask.ext.cors import CORS, cross_origin
from bson import json_util
from pipelines import MONGODBPipeline
from datetime import datetime
from yahoo_finance import Share
from settings import ACCESS_TOKEN
import unirest
import pytz
from misc.stock_processing import hottness_function, bs_function
# App config
app = Flask(__name__)
app.config.from_object(__name__)
# Cors Config
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# Create Database Stock
db = MONGODBPipeline()

# -------- Stock Infos --------
# API CIC(Collection Infos Create)


@app.route('/cic')
def createInfos():
    if db.infos.count() == 0:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('static/sp100.json', 'rb') as f:
            ls = json.load(f)
            for i in ls:
                symbol = Share(i['name'])
                item = {}
                item['name'] = i['name']
                item['price'] = symbol.get_price()
                item['time'] = timestamp
                item['prev_close'] = symbol.get_prev_close()
                item['open'] = symbol.get_open()
                item['volume'] = symbol.get_volume()
                item['pe'] = symbol.get_price_earnings_ratio()
                item['eps'] = symbol.get_earnings_share()
                item['price_sales'] = symbol.get_price_sales()
                item['ebitda'] = symbol.get_ebitda()
                item['hottness'] = "NA"
                item['B/S'] = "NA"
                db.infos.insert_one({
                    "name": i['name'],
                    "sector": i['sector'],
                    "data": [item]
                })
        print('Collection Infos Created.')
        return Response('Collection Infos Created.')
createInfos()
# API CIU(Collection Iinfo Update)


@app.route('/ciu')
def updateInfos():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        for i in ls:
            symbol = Share(i['name'])
            item = {}
            item['name'] = i['name']
            item['price'] = symbol.get_price()
            item['time'] = timestamp
            item['prev_close'] = symbol.get_prev_close()
            item['open'] = symbol.get_open()
            item['volume'] = symbol.get_volume()
            item['pe'] = symbol.get_price_earnings_ratio()
            item['eps'] = symbol.get_earnings_share()
            item['price_sales'] = symbol.get_price_sales()
            item['ebitda'] = symbol.get_ebitda()
            item['hottness'] = "NA"
            item['B/S'] = "NA"
            db.infos.update(
                {"name": i['name']},
                {
                    "$push": {"data": item}
                }
            )
    print('Collection Infos updated.')
    return Response('Collection Infos updated.')
# API CID(Collection Infos Delete)
# Only for Debug Use


@app.route("/cid")
def deleteInfos():
    db.infos.delete_many({})
    return Response('Collection Infos deleted.')

# --------- Stock Twits ----------
# API CTC(Collection Twits Create)


@app.route('/ctc')
def createTwits():
    if db.twits.count() == 0:
        with open('static/sp100.json', 'rb') as f:
            ls = json.load(f)
            unirest.timeout(20)
            url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json?access_token={}"
            for i in ls:
                response = unirest.get(url.format(
                    i['name'], ACCESS_TOKEN))
                data = response.body
                msgs = data['messages']
                items = []
                for msg in msgs:
                    item = {}
                    item['name'] = msg['user']['username']
                    item['body'] = msg['body']
                    item['id'] = msg['id']
                    time = datetime.strptime(
                        msg['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                    utc = pytz.utc
                    item['time'] = utc.localize(time).astimezone(
                        pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
                    item['symbols'] = [i['symbol'] for i in msg['symbols']]
                    item['reshares'] = msg['reshares']['reshared_count']
                    item['b/s'] = msg['entities']['sentiment']
                    items.append(item)
                db.twits.ensure_index("id", unique=True)
                db.twits.insert_many(items)
            return Response('Collection Twits Created.')

createTwits()
# API CTU(Collection Twits Update)


@app.route('/ctu')
def updateTwits():
    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        url = "https://api.stocktwits.com/api/2/streams/symbol/{}.json?access_token={}"
        for i in ls:
            unirest.timeout(20)
            response = unirest.get(url.format(
                i['name'], ACCESS_TOKEN))
            data = response.body
            msgs = data['messages']
            items = []
            for msg in msgs:
                item = {}
                item['name'] = msg['user']['username']
                item['body'] = msg['body']
                item['id'] = msg['id']
                time = datetime.strptime(
                    msg['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                utc = pytz.utc
                item['time'] = utc.localize(time).astimezone(
                    pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %H:%M:%S')
                item['symbols'] = [i['symbol'] for i in msg['symbols']]
                item['reshares'] = msg['reshares']['reshared_count']
                item['b/s'] = msg['entities']['sentiment']
                items.append(item)
            db.twits.ensure_index("id", unique=True)
            db.twits.insert_many(items)
    return Response('Collection Twits updated.')
# API CTD(Collection Twits Delete)


@app.route("/ctd")
def deleteTwits():
    db.twits.delete_many({})
    return Response('Collection Twits Deleted.')

# ===============API GET===============

# Route for homepage


@app.route("/")
def home():
    return render_template("home.html", name="home")
# Route for getting symbol within sector


@app.route("/sectors", methods=["GET"])
@cross_origin()
def section():
    if not('sector' in request.args) or (request.args['sector'] == 'All'):
        sector = "S&P 100 Index Symbols"
        data = [i['data'][len(i['data']) - 1]
                for i in db.infos.find()]
        return Response(json.dumps({sector: data}, default=json_util.default),
                        mimetype='application/json')

    else:
        sector = request.args['sector'][
            0].upper() + request.args['sector'][1:] + " Sector Symbols"
        data = [i['data'][len(i['data']) - 1] for i in db.info_collection.find(
            {'sector': request.args['sector']})]
        return Response(json.dumps({sector: data}, default=json_util.default),
                        mimetype='application/json')
# Route for searching specific symbol and it's general information


@app.route("/search", methods=["GET"])
@cross_origin()
def search():
    name = request.args['symbol']
    data = [i for i in db.infos.find(
        {'name': name})]
    return Response(json.dumps({'data': data}, default=json_util.default),
                    mimetype='application/json')
# Route for searching specific symbol and return it's twits


@app.route("/twits", methods=["GET"])
@cross_origin()
def twits():
    if not('symbol' in request.args) or (request.args['symbol'] == 'All'):
        data = [i for i in db.twits.find(
            {}, projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(30)]
        return Response(json.dumps({'data': data}, default=json_util.default),
                        mimetype='application/json')
    else:
        name = request.args['symbol']
        data = [i for i in db.twits.find(
            {"symbols": {"$elemMatch": {"$eq": name}}},
            projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(30)]
    return Response(json.dumps({'data': data}, default=json_util.default),
                    mimetype='application/json')
# Route for getting price for specific symbol.


@app.route('/price', methods=["GET"])
@cross_origin()
def price():
    pass
# Error Handler


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    return Response(json.dumps(message, default=json_util.default), mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
