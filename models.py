import datetime
from collections import namedtuple, OrderedDict

from pymongo import MongoClient
from pymongo.errors import OperationFailure

from config import get_redis


class MongoCfg(object):
    def __init__(self, host, port, db, expire=600, tz=8*60*60):
        mc = MongoClient(host, port)
        self.db = mc[db]
        self.expire = int(expire)
        self.tz = tz


class MongoResult(dict):
    def __init__(self, tz, **kwargs):
        created_at = kwargs.pop('created_at')
        for k, v in kwargs.items():
            self[k] = v
        self['created_at'] = created_at + datetime.timedelta(seconds=tz)


class BaseModel(object):
    def __init__(self, mcfg, col):
        self.tz = mcfg.tz
        self.col = mcfg.db[col]
        try:
            if 'created_at_1' in self.col.index_information():
                if self.col.index_information()['created_at_1'].get('expireAfterSeconds', 0) != mcfg.expire:
                    self.col.drop_index('created_at_1')
                    print('recreated index of "created_at"')
                    self.col.create_index([("created_at", 1)], expireAfterSeconds=mcfg.expire)
            else:
                print('created index of "created_at"')
                self.col.create_index([("created_at", 1)], expireAfterSeconds=mcfg.expire)
        except OperationFailure:
            print('created index of "created_at"')
            self.col.create_index([("created_at", 1)], expireAfterSeconds=mcfg.expire)

    def get_all(self):
        queryset = self.col.find().sort([('created_at', 1)])
        return None if queryset is None else (MongoResult(self.tz, **q) for q in queryset)

    def get(self, utc_ts):
        if not isinstance(utc_ts, datetime.datetime):
            utc_ts = float(utc_ts)
            utc_ts = datetime.datetime.fromtimestamp(utc_ts)
        queryset = self.col.find({'created_at': {'$gt': utc_ts}}).sort([('created_at', 1)])
        queryset = (MongoResult(self.tz, **q) for q in queryset)
        return queryset


class CPUModel(BaseModel):
    _fields = ['id', 'user', 'nice', 'system', 'iowait', 'irq', 'softirq',
               'steal', 'guest', 'guest_nice', 'created_at']

    def __init__(self, mcfg):
        col = 'cpu'
        super(CPUModel, self).__init__(mcfg, col)

    def save(self, **key):
        post = dict([(f, float(key.get(f, 0))) for f in self._fields])
        post.pop('id')
        post['created_at'] = datetime.datetime.utcnow()
        self.col.insert(post)


class RAMModel(BaseModel):
    _fields = ['id', 'available', 'used', 'free', 'active', 'inactive', 'buffers', 'cached', 'shared']
    def __init__(self, mcfg):
        col = 'ram'
        super(RAMModel, self).__init__(mcfg, col)

    def save(self, **key):
        post = dict([(f, int(key.get(f, 0))) for f in self._fields])
        post.pop('id')
        post['created_at'] = datetime.datetime.utcnow()
        self.col.insert(post)
