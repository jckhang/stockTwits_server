import pymongo
from functools import wraps
import errno
import os
import signal


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DB = "heroku_6nk70pz9"
MONGODB_COLLECTION = ["infos", "twits", "keywords"]
ACCESS_TOKEN = "df4ffc6a2c51746f854034739a446a86f723f9eb"


class MONGODBPipeline(object):

    def __init__(self):
        if os.getenv('MONGOLAB_URI') is not None:
            connection = pymongo.MongoClient(
                "mongodb://user:123@ds061974.mlab.com:61974/heroku_6nk70pz9"
            )
            print "connect heroku"
        else:
            connection = pymongo.MongoClient(
                MONGODB_URI
                # "mongodb://user:123@ds061974.mlab.com:61974/heroku_6nk70pz9"
            )
            print "connect local"
        db = connection[MONGODB_DB]
        self.infos = db[MONGODB_COLLECTION[0]]
        self.twits = db[MONGODB_COLLECTION[1]]
        self.keywords = db[MONGODB_COLLECTION[2]]
        print('------ Connection succeed! -------')
