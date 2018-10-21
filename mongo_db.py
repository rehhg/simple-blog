import os
from abc import ABCMeta
from pymongo import MongoClient
from bson.objectid import ObjectId


ABC = ABCMeta('ABC', (object,), {'__slots__': ()})


class AbstractClient(ABC):
    pass


class MongoDBClient(AbstractClient):
    PAGE_SIZE = 5

    def __init__(self):
        self.client = MongoClient('db', 27017)
        self.db_table = self.client.test
        self.db_table.users.insert({'name': 'root', 'password': 'root', 'role': 'admin'})

    def get_lists(self, page=1):
        skip = (page - 1) * self.PAGE_SIZE
        return self.db_table.posts.find().skip(skip).limit(self.PAGE_SIZE).sort('_id', -1)

    def create_post(self, data):
        return self.db_table.posts.insert(data)

    def delete_post(self, post_id):
        return self.db_table.posts.remove({'_id': ObjectId(post_id)})

    def get_post(self, post_id):
        return self.db_table.posts.find_one({'_id': ObjectId(post_id)})

    def update(self, post_id, data):
        return self.db_table.posts.update({'_id': ObjectId(post_id)}, {'$set': data})

    def get_total_page(self):
        return self.db_table.posts.count() / self.PAGE_SIZE + 1

    def find_user(self, user: dict):
        return self.db_table.users.find_one(user)
