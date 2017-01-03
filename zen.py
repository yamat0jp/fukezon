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
        ident = u''
        s = self.get_argument('search','')
        if s:
            data = self.application.db.all(where('name') == s)
        else:
            detail = self.get_argument('detail','')
            if detail:
                data = self.application.db.get(where('name') == detail)
                self.render('modules/main2.html',items=items,new=new,id=ident,number=3,data=data)
                return
            data = self.application.db.all()
        self.render('modules/main.html',items=items,new=new,cart=cart,id=ident,number=5,data=data)
           
class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        self.redirect(r'/main')
        
class UserHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('user.html')
        
class CartHandler(tornado.web.RequestHandler):
    def get(self):
        items = TinyDB('static/db/cart.json').all()
        table = self.application.db
        data = []
        for x in items:
            temp = table.get(where('id') == x['id'])
            for y in data:
                if y['id'] == temp['id']:
                    y['count'] += 1
                else:
                    data.append(temp)
        self.render('cartitem.html',data=data)
        
class DeleteHandler(tornado.web.RequestHandler):
    def get(self):
        ident = self.get_argument('id','')
        if ident:
            self.application.db.remove(where('id') == ident)
        
class RegistHandler(tornado.web.RequestHandler):
    def post(self):
        data = TinyDB('static/db/user.json')
        info = {}
        info['name'] = self.get_arguments('name')
        info['birth'] = self.get_argument('birth')
        info['email'] = self.get_argument('email')
        info['address'] = self.get_argument('address','')
        info['password'] = self.get_argument('password')
        data.insert(info)
        self.redirect(r'/main')
        
class PayHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('payment.html')
        
class SendHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(r'/main')
        
class ItemHandler(tornado.web.RequestHandler):
    def get(self):
        item = TinyDB('static/db/temp.json').all()
        table = self.application.db
        ident = self.get_argument('id','')
        if ident:
            index = table.get(where('id') == ident)
        else:
            index = {'id':0,'name':'','price':0,'weight':0,'maker':'','category':'',
                     'stock':0,'active':True,'url':'http://'}
        self.render('item.html',item=item,data=table.all(),index=index)
               
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
        handlers =[(r'/main',IndexHandler),(r'/login',LoginHandler),(r'/user',UserHandler),(r'/register',RegistHandler),
                   (r'/item',ItemHandler),(r'/cart',CartHandler),(r'/payment',PayHandler),(r'/[a-zA-Z0-9]*',SendHandler)]
        setting = {'template_path':os.path.join(os.path.dirname(__file__),'templates'),
                   'static_path':os.path.join(os.path.dirname(__file__),'static'),
                   'ui_modules':{'mybox':BoxModule,'mycart':CartModule,'mycount':CountModule,'login':LoginModule},
                   'debug':True}
        tornado.web.Application.__init__(self,handlers,**setting)
    
app = Application()    
if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
