'''
Created on 2016/12/29

@author: fukemasashi
'''
import os.path
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tinydb import *


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        items = ['book','soft','drink']
        new = ['coffee','tea']
        cart = {'book':3000,'soft':15000}
        ident = ''
        detail = self.get_argument('detail','')
        if detail:
            data = self.application.db.table('data').get(where('name') == detail)
            self.render('modules/main2.html',items=items,new=new,id=ident,number=3,data=data)
        else:
            data = self.application.db.table('data').all()
            self.render('modules/main.html',items=items,new=new,cart=cart,id=ident,number=5,data=data)
    
class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(r'/')
        
class UserHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('user.html')
               
class BoxModule(tornado.web.UIModule):
    def render(self,items):
        return self.render_string('modules/box.txt',items=items)
    
class CartModule(tornado.web.UIModule):
    def render(self,items):
        return self.render_string('modules/cart.txt',items=items)
    
class CountModule(tornado.web.UIModule):
    def render(self,number):
        return self.render_string('modules/count.txt',number=number)
    
class LoginModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('modules/login.txt')
    
class Application(tornado.web.Application):
    def __init__(self):
        self.db = TinyDB('static/db/db.json')
        handlers =[(r'/main',IndexHandler),(r'/login',LoginHandler),(r'/user',UserHandler)]
        setting = {'template_path':os.path.join(os.path.dirname(__file__),'templates'),
                   'static_path':os.path.join(os.path.dirname(__file__),'static'),
                   'ui_modules':{'mybox':BoxModule,'mycart':CartModule,'mycount':CountModule,'login':LoginModule},
                   'debug':True}
        tornado.web.Application.__init__(self,handlers,**setting)
        
        
http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(8000)
tornado.ioloop.IOLoop.instance().start()
