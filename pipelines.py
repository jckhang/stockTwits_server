import pymongo
import os
import settings


class MONGODBPipeline(object):
    def __init__(self):
        if os.getenv('MONGOLAB_URI') is not None:
            connection = pymongo.MongoClient(
                "mongodb://user:123@ds061974.mlab.com:61974/heroku_6nk70pz9"
            )
            print "connect heroku"
        else:
            connection = pymongo.MongoClient(
                # settings.MONGODB_URI
                "mongodb://user:123@ds061974.mlab.com:61974/heroku_6nk70pz9"
            )
            print "connect local"
        db = connection[settings.MONGODB_DB]
        self.info_collection = db[settings.MONGODB_COLLECTION[0]]
        self.twits_collection = db[settings.MONGODB_COLLECTION[1]]
        self.keywords_collection = db[settings.MONGODB_COLLECTION[2]]
        print('------ Connection succeed! -------')
