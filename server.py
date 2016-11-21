import os

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import options, define

from config import get_web

define('debug', default=True, help='enable debug mode')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        plugins = [{'title': 'CPU'}, {'title': 'Memary'}]
        self.render('index.html', plugins=plugins)


class PluginModule(tornado.web.UIModule):
    def render(self, plugin):
        return self.render_string('modules/plugin.html', plugin=plugin)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
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
