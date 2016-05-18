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
        {}, projection={"_id": 0, "id": 0, "reshares": 0}).sort('time', -1)
    result = [symbol in i['symbols'] for i in cursor]
    # print(result)
    return "%.2f" % (sum(result) / db.twits.count())

# Calculate the B/S ratio of #symbol. Look at the newest 1000 twits and average
# the sentiment score of each twit. "NULL" is treated as 0, "Bearish" as -1,
# and "Bullish" as 1.
# Parameters:
#   Input: symbol name
#   Output: average sentiment score


def bs_function(symbol):
    cursor = db.twits.find(
        {"symbols": {"$elemMatch": {"$eq": symbol}}},
        projection={"_id": 0, "id": 0, "reshares": 0}).sort("time", -1).limit(1000)
    result = [i['bs'] for i in cursor]
    return "%.4f" % (sum(result) / 1000)


def regex(st):
    import re
    # Remove $ tags
    st_re = re.sub(r'(?i)\$\w+', "", st)
    # Remove unicode start with \
    st_re = re.sub(r'(?i)\\\w+', "", st_re)
    # Remove @ tag
    st_re = re.sub(r'(?i)\@\w+', "", st_re)
    # Remove html special symbols
    st_re = re.sub(r'(?i)\&\w+', "", st_re)
    # Remove https
    st_re = re.sub('((www\.[\s]+)|https?://[^\s]+)', "", st_re)
    return st_re.split(" ")
