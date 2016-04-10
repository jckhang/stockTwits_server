from flask import Flask
from flask import render_template
from flask import request
from flask import json
from flask import jsonify
from flask import Response
from bson import json_util
from pipelines import MONGODBPipeline


app = Flask(__name__)
app.config.from_object(__name__)
db = MONGODBPipeline()

@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/sectors", methods=["GET"])
def section():
    if not('sector' in request.args) or (request.args['sector']=='all'):
        sector = "S&P 100 Index Symbols"
        data = [i for i in db.info_collection.find()]
        return Response(json.dumps({sector: data}, default=json_util.default),
                mimetype='application/json')

    else:
        sector = request.args['sector'][0].upper()+request.args['sector'][1:]+ " Sector Symbols"
        data = [i for i in db.info_collection.find({'sector':request.args['sector']})]
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
