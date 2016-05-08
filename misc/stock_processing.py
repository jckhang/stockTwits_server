from __future__ import division
from settings import MONGODBPipeline
db = MONGODBPipeline()
# Calculate the hottness of #symbol. Look at the newest 1000 twits and sum up
# the number of twits that contain that symbol.
# Parameters:
#   Input: symbol name
#   Output: normalized hotness(divide by 1000)


def hotness_function(symbol):
    cursor = db.twits.find(
        {}, projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1).limit(1000)
    result = [symbol in i['symbols'] for i in cursor]
    return "%.2f" % (sum(result) / 10)

# Calculate the B/S ratio of #symbol. Look at the newest 1000 twits and average
# the sentiment score of each twit. "NULL" is treated as 0, "Bearish" as -1,
# and "Bullish" as 1.
# Parameters:
#   Input: symbol name
#   Output: average sentiment score


def bs_function(symbol):
    def bs(record):
        if record is None:
            return 0
        else:
            return 1 if record['basic'] == "Bullish" else -1
    cursor = db.twits.find(
        {"symbols": {"$elemMatch": {"$eq": symbol}}},
        projection={"_id": 0, "id": 0, "reshares": 0}).sort("time", -1).limit(1000)
    result = [bs(i['bs']) for i in cursor]
    return "%.4f" % (sum(result) / 1000)
