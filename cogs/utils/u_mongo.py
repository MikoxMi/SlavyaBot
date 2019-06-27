from pymongo import MongoClient
import os

class Mongo():
    def __init__(self):
        self.url = str(os.getenv('URL_MONGO'))
        self.port = str(os.getenv('PORT'))
        self.client = MongoClient(host=self.url, port=self.port, connectTimeoutMS=30000, serverSelectionTimeoutMS=10, connect=False)
        self.db = self.client.get_database("weekbd")
        self.collections = {'members': self.db.members,
                            'server_settings': self.db.server_settings,
                            'shop': self.db.shop,
                            'member_profile': self.db.member_profile}

    @staticmethod
    async def get_record(collection:str, name:str, value):
        """
        Get custom record
        """
        m = Mongo()
        record = m.collections[collection].find_one({name: value})
        return record

    @staticmethod
    async def get_record_option(collection: str, category: str, name: str):
        """
        Get record with sort(name)
        """
        m = Mongo()
        record = m.collections[collection].find({category: { "$regex": F"^{name}", '$options': 'i'}})
        return record

    @staticmethod
    async def get_record_more(collection:str, name:str, value):
        """
        Get more record if 'name' is found
        """
        m = Mongo()
        record = m.collections[collection].find({name: value})
        return record

    @staticmethod
    async def get_record_find(collection: str):
        """
        Get all items
        """
        m = Mongo()
        record = m.collections[collection].find()
        return record

    @staticmethod
    async def get_record_sort(collection: str, value: str, arg: int):
        """ Get record with sort
        '-1' - DESCENDING
        '1' -  ASCENDING
        """
        m = Mongo()
        record = m.collections[collection].find().sort(value, arg)
        return record

    @staticmethod
    async def update_record(collection:str, record, upg):
        """
        Update record for one member
        """
        m = Mongo()
        m.collections[collection].update_one({'_id': record['_id']}, {'$set': upg})

    @staticmethod
    async def update_all(collection: str, upg):
        """
        Update all records
        """
        m = Mongo()
        m.collections[collection].update({}, {'$set': upg}, multi=True)

    @staticmethod
    async def delete_record(collection: str, category: str, value: str):
        """
        Delete record
        """
        m = Mongo()
        m.collections[collection].delete_one({category: value})

    @staticmethod
    async def record_insert(collection:str, upg):
        """
        Insert new record
        """
        m = Mongo()
        m.collections[collection].insert_one(upg)

    