import pymongo
import settings


class MONGODBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings.MONGODB_HOST,
            settings.MONGODB_PORT
        )
        db = connection[settings.MONGODB_DB]
        self.info_collection = db[settings.MONGODB_COLLECTION[0]]
        self.twits_collection = db[settings.MONGODB_COLLECTION[1]]
        self.keywords_collection = db[settings.MONGODB_COLLECTION[2]]
        print('------ Connection succeed! -------')
