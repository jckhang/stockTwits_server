from flask import Flask
from flask import render_template
from flask import request
from flask import json
from flask import jsonify
from flask import Response
from bson import json_util
from pipelines import MONGODBPipeline
from datetime import datetime
from yahoo_finance import Share


app = Flask(__name__)
app.config.from_object(__name__)
db = MONGODBPipeline()
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if db.info_collection.count() == 0:
    with open('static/sp100.json', 'rb') as f:
        ls = json.load(f)
        for i in ls:
            symbol = Share(i['name'])
            i['price'] = symbol.get_price()
            i['time'] = timestamp
            i['prev_close'] = symbol.get_prev_close()
            i['open'] = symbol.get_open()
            i['volume'] = symbol.get_volume()
            i['price_earnings_ratio'] = symbol.get_price_earnings_ratio()
            i['price_sales'] = symbol.get_price_sales()
            i['ebitda'] = symbol.get_ebitda()
            i['hottness'] = "NA"
            i['B/S'] = "NA"
    result = db.info_collection.insert_many(ls)


@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/sectors", methods=["GET"])
def section():
    if not('sector' in request.args) or (request.args['sector'] == 'all'):
        sector = "S&P 100 Index Symbols"
        data = [i for i in db.info_collection.find()]
        return Response(json.dumps({sector: data}, default=json_util.default),
                        mimetype='application/json')

    else:
        sector = request.args['sector'][
            0].upper() + request.args['sector'][1:] + " Sector Symbols"
        data = [i for i in db.info_collection.find(
            {'sector': request.args['sector']})]
        return Response(json.dumps({sector: data}, default=json_util.default),
                        mimetype='application/json')


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
