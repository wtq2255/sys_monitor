import datetime
from collections import namedtuple, OrderedDict

from pymongo import MongoClient

from config import get_redis


class MongoCfg(object):
    def __init__(self, host, port, db):
        mc = MongoClient(host, port)
        self.db = mc[db]


class BaseModel(object):
    def __init__(self, mcfg, col):
        self.col = mcfg.db[col]

    def _format(self, val):
        _id = val.pop('_id')
        val['id'] = _id
        return self.Result(OrderedDict(sorted(val.items(), key=lambda x: self._fields.index(x[0]))))

    def get_all(self):
        queryset = self.col.find().sort([('created', 1)])
        if queryset:
            for val in queryset:
                yield val
                # yield self._format(val)
        else:
            return None

    def get(self, ts):
        if not isinstance(ts, datetime):
            ts = datetime.datetime.fromtimestamp(ts)
        queryset = self.col.find({'created_at': {'$gt': ts}})


class CPUModel(BaseModel):
    _fields = ['id', 'count', 'user', 'nice', 'system', 'idle', 'iowait', 'irq',
               'softirq', 'steal', 'guest', 'guest_nice', 'created_at']
    Result = namedtuple('CPU', _fields)

    def __init__(self, mcfg):
        col = 'cpu'
        super(CPUModel, self).__init__(mcfg, col)

    def save(self, **key):
        post = dict([(f, float(key.get(f, 0))) for f in self._fields])
        print(post)
        post.pop('id')
        post['created_at'] = datetime.datetime.now()
        self.col.insert(post)
