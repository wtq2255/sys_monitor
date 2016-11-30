import os
import json
import threading
from collections import defaultdict

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define, parse_command_line

from config import get_web, get_monitor
from monitor import CPUMonitor, RAMMonitor
from monitor import main as monitor_main

define('debug', default=True, help='enable debug mode')

_categorys = {
    'cpu': CPUMonitor(),
    'ram': RAMMonitor()
}


def format_series(datas):
    series = defaultdict(lambda: list())
    for data in datas:
        data.pop('_id')
        created_at = data.pop('created_at').strftime('%Y-%m-%d %H:%M:%S')
        for name, val in data.items():
            series[name].append([created_at, val])
    return dict(series)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        categorys = get_monitor('category').strip().split(',')
        interval = int(get_monitor('interval'))
        expire = int(get_monitor('expire'))
        plugins = [{'title': c} for c in categorys]
        self.render('index.html', plugins=plugins, interval=interval, expire=expire)


class PluginModule(tornado.web.UIModule):
    def render(self, plugin):
        return self.render_string('modules/plugin.html', plugin=plugin)


class PluginsHandler(tornado.web.RequestHandler):

    def get(self, plugin):
        utc_ts = float(self.get_argument('utc_ts', None))
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if utc_ts < int(get_monitor('interval')):
            datas = _categorys[plugin.lower()].get()
            series = format_series(datas)
            legend = series.keys()
            self.render('options/percent.json', title=plugin, legend=legend, series=series)
        else:
            data = _categorys[plugin.lower()].get_one(utc_ts)
            data = format_series([data])
            data = json.dumps(data)
            self.write(data)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/plugin/(.*)", PluginsHandler),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            # xsrf_cookies=True,
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            # login_url="/auth/login",
            ui_modules={'Plugin': PluginModule},
            debug=options.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    monitor_run()
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    # 监听端口
    http_server.listen(get_web('port'), get_web('host'))
    # 启动服务
    tornado.ioloop.IOLoop.instance().start()

def monitor_run():
    t = threading.Thread(target=monitor_main)
    t.start()

if __name__ == "__main__":
    main()
