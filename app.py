from flask import Flask
from flask import render_template
from flask import request
from flask import json
from flask import jsonify
from flask import Response
from flask.ext.cors import CORS, cross_origin
from bson import json_util
from pipelines import MONGODBPipeline
from datetime import datetime
from yahoo_finance import Share
from settings import ACCESS_TOKEN
import unirest

# Create Database Stock
app = Flask(__name__)
app.config.from_object(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = MONGODBPipeline()

# -------- Stock Symbol --------
# Create stock symbol


@app.route('/dbsc')
def createDBstock():
    if db.info_collection.count() == 0:
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
                db.info_collection.insert_one({
                    "name": i['name'],
                    "sector": i['sector'],
                    "data": [item]
                })
    return Response('Collection Info created.')
createDBstock()
# Update Stock database


@app.route('/dbsu')
def updateDBstock():
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
            db.info_collection.update(
                {"name": i['name']},
                {
                    "$setOnInsert": {"data": item}
                }
            )
    return Response('Collection Info updated.')
# Delete the record in stock database


@app.route("/dbsd")
def deleteDBstock():
    db.info_collection.delete_many({})
    return Response('Collection Info deleted.')

# --------- StockTwits ----------
# Create Twits database


@app.route('/dbtc')
def createDBtwits():
    if db.twits_collection.count() == 0:
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
                    item['time'] = msg['created_at']
                    item['symbols'] = [i['symbol'] for i in msg['symbols']]
                    item['reshares'] = msg['reshares']['reshared_count']
                    items.append(item)
                db.twits_collection.ensure_index("id", unique=True)
                db.twits_collection.insert_many(items)
    return Response('Collection Twits Created.')

createDBtwits()
# Update Twits database
#


@app.route('/dbtu')
def updateDBtwits():
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
                item['time'] = msg['created_at']
                item['symbols'] = [i['symbol'] for i in msg['symbols']]
                item['reshares'] = msg['reshares']['reshared_count']
                items.append(item)
            db.twits_collection.ensure_index("id", unique=True)
            db.twits_collection.insert_many(items)
    return Response('Collection Twits updated.')
# Delete the record in twits database


@app.route("/dbtd")
def deleteDBtwits():
    db.twits_collection.delete_many({})
    return Response('Collection Twits deleted.')
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
                for i in db.info_collection.find()]
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
    data = [i for i in db.info_collection.find({'name': name})]
    return Response(json.dumps({'data': data}, default=json_util.default),
                    mimetype='application/json')
# Route for searching specific symbol and return it's twits


@app.route("/twits", methods=["GET"])
@cross_origin()
def twits():
    if not('symbol' in request.args) or (request.args['symbol'] == 'All'):
        data = [i for i in db.twits_collection.find(
            {}, projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(30)]
        return Response(json.dumps({'data': data}, default=json_util.default),
                        mimetype='application/json')
    else:
        name = request.args['symbol']
        data = [i for i in db.twits_collection.find(
            {"symbols": {"$elemMatch": {"$eq": name}}},
            projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(30)]
        return Response(json.dumps({'data': data}, default=json_util.default),
                        mimetype='application/json')
# Error Handler


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

if __name__ == "__main__":
    app.run(debug=True)
