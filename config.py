from configparser import ConfigParser


cf = ConfigParser()
cf.read('./sys_monitor.conf')


def get(section, option=None):
    if option is None:
        results = {}
        for k, v in cf.items(section):
            results[k] = int_format(v)
    else:
        results = int_format(cf.get(section, option))
    return results

def int_format(msg):
    if msg.isdigit() or (msg.startswith('-') and msg[1:].isdigit()):
        msg = int(msg)
    return msg


def get_web(field=None):
    return get('web', field)


def get_redis(field=None):
    return get('redis', field)


def get_mongo(field=None):
    return get('mongo', field)


def get_monitor(field=None):
    return get('monitor', field)
