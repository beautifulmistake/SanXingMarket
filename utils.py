import pymongo

MONGO_URL = "mongodb://admin:admin@IP:port"
MONGO_DB_NAME = "f_sanxing"
MONGO_IP = "localhost"
MONGO_PORT = 27017
RESULT_COLLECTIONS_NAME = "sanxing_result"  # 表名


def get_db():
    # mongo_uri = 'mongodb://wb_zyym:orange123@39.105.31.96:27017/all_project_xxc'
    # mongo_db = pymongo.MongoClient(mongo_uri)
    # return mongo_db.get_database("all_project_xxc")

    # mongo_client = pymongo.MongoClient(MONGO_IP, MONGO_PORT)
    # return mongo_client[MONGO_DB_NAME]
    mongo_db = pymongo.MongoClient(MONGO_URL)
    return mongo_db[MONGO_DB_NAME]
