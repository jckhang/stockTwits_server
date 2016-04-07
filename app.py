from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from bson.json_util import dumps
from pipelines import MONGODBPipeline


app = Flask(__name__)
app.config.from_object(__name__)
db = MONGODBPipeline()


@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/symbol", methods=["GET"])
def stocks():
    resp = dumps([i for i in db.info_collection.find({})])
    return resp


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
