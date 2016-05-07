from settings import ACCESS_TOKEN, MONGODBPipeline
db = MONGODBPipeline()
print ACCESS_TOKEN
# Calculate the hottness of #symbol. The basic approach is to sum up the total
# number of twits that contain that symbol.


def hottness_function(symbol):
    data = [i['data'][-10:] for i in db.infos.find({'name': symbol})]
    return "NA"

# Calculate the B/S ratio of #symbol. The basic approach is to average the sent-
# iment score of each twit.


def bs_function(symbol):
    return "NA"
