import os
import json
from collections import defaultdict

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define, parse_command_line

from config import get_web, get_monitor
from monitor import CPUMonitor

define('debug', default=True, help='enable debug mode')

_categorys = {
    'cpu': CPUMonitor(),
    'ram': CPUMonitor()
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
        plugins = [{'title': c} for c in categorys]
        self.render('index.html', plugins=plugins)


class PluginModule(tornado.web.UIModule):
    def render(self, plugin):
        return self.render_string('modules/plugin.html', plugin=plugin)


class PluginsHandler(tornado.web.RequestHandler):

    def get(self, plugin):
        ts = self.get_argument('ts', None)
        datas = _categorys[plugin.lower()].get(ts)
        series = format_series(datas)
        legend = list(series.keys())
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        js = self.render_string('options/normal.json', title=plugin, legend=legend, series=series)
        print(type(js))
        print(json.loads(js))
        self.write(json.dumps({'a': 1}))
        # self.write(js)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/plugin/(.*)", PluginsHandler),
        ]

        settings = dict(
            blog_title='sys monitor',
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
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    # 监听端口
    http_server.listen(get_web('port'), get_web('host'))
    # 启动服务
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
