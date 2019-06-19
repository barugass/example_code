from tornado import web, ioloop
import tornado.websocket
import subprocess
import configparser
import requests
import json

config = configparser.ConfigParser()
config.read('configurate.ini')
dict_conf = config['Configuratetornado']
PORT = dict_conf['Port']
DIRECTORY = dict_conf['Directory']


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", ChatScaner),
            (r"/scaner/", MainHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            xsrf_cookies=True,
        )
        super(Application, self).__init__(handlers, **settings)


class MainHandler(web.RequestHandler):
    def get(self):
        save_code = self.get_arguments("code")
        list_id = self.get_arguments("list_scan_id")
        server = ioloop.IOLoop.current()
        server.add_callback(ChatScaner.send_message, save_code, list_id)
        self.set_status(200)
        self.finish()


class ChatScaner(tornado.websocket.WebSocketHandler):
    waiters = None
    id_save = {}
    check_code = {}
    list_scan_id = {}

    def check_origin(self, origin):
        return True

    def open(self):
        if ChatScaner.waiters is None:
            ChatScaner.waiters = self
        else:
            self.check_code = {'code': 130}
            self.write_message(json.dumps(self.check_code))
            self.close()
            
    @classmethod
    def send_message(cls, messsage, data=None):
        send_code = int(messsage[0])
        send_data = {'code': send_code}
        if data is not None:
            send_data['list_scan_id'] = data
        try:
            cls.waiters.write_message(json.dumps(send_data))
        except:
            pass

    def on_message(self, messsage):
        self.id_save = json.loads(messsage)
        try:
            subprocess.Popen([DIRECTORY, self.id_save['id_res'], self.id_save['id_com'], self.id_save['type_scan']])
        except KeyError as e:
            self.check_code = {'code': 140}
            self.write_message(json.dumps(self.check_code))

    def on_close(self):
        if ChatScaner.waiters is self:
            ChatScaner.waiters = None
        

if __name__ == '__main__':
    app = Application()
    app.listen(PORT, address="0.0.0.0")
    ioloop.IOLoop.current().start()
    
    
