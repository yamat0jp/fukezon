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
        self.application.back = False
        items = ['book','soft','drink']
        new = ['coffee','tea']
        cart = {'book':3000,'soft':15000}
        user = self.application.ident
        if user:
            ident = user['name']
        else:
            ident = 'guest'
        s = self.get_argument('search','')
        if s:
            data = self.application.db.contains(where('name') == s)
        else:
            detail = self.get_argument('detail','')
            if detail:
                data = self.application.db.contains(where('name') == detail)
                self.render('modules/main2.html',items=items,new=new,id=ident,number=3,data=data)
                return
            data = self.application.db.all()
        self.render('modules/main.html',items=items,new=new,cart=cart,id=ident,number=5,data=data)
           
class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        table = self.application.db.table('user')
        email = self.get_argument('email')
        word = self.get_argument('password')
        query = (where('email') == email)&(where('password') == word)
        self.application.ident = table.get(query)
        self.redirect(r'/main')
        
    def get(self):
        self.application.ident = {}
        self.redirect(r'/main')
        
class UserHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('user.html')
        
    def post(self):
        info = {}
        info['name'] = self.get_argument('name')
        info['email'] = self.get_argument('email')
        info['address'] = self.get_argument('address','')
        info['password'] = self.get_argument('password')
        table = self.application.db.table('user')
        if table.contains(where('email') == info['email']) == False:
            eid = table.insert(info)
            table.update({'ident':eid},eids=[eid])
            self.application.ident = table.get(eid=eid)
            if self.application.back:
                self.redirect(r'/cart')
            else:
                self.redirect(r'/main')
        else:
            self.redirect(r'/user')
            
class CartHandler(tornado.web.RequestHandler):
    def get(self):
        if self.application.ident == {}:
            self.application.back = True
            self.redirect(r'/user')
            return
        table = self.application.db.table('cart')
        data = table.search(where('ident') == self.application.ident['ident'])
        self.render('cartitem.html',data=data)
        
    def post(self):
        ident = self.get_argument('id')
        count = self.get_argument('count')
        table = self.application.db.table('cart')
        user = self.application.ident
        if user:
            q = Query()
            query = (q.ident == user['ident'])&(q.item_id == ident)
            if table.contains(query):
                el = table.get(query)
                table.update({count:el['count']+count},eids=[el.eid])
            else:
                table.insert({'ident':ident,'count':count})
        else:
            eid = table.insert({'ident':0,'item_id':ident,'count':count})
            self.redirect(r'/main')
                
class DeleteHandler(tornado.web.RequestHandler):
    def get(self):
        ident = self.get_argument('id','')
        if ident:
            self.application.db.remove(where('id') == ident)
              
class PayHandler(tornado.web.RequestHandler):
    def get(self):
        ident = self.application.ident
        if ident:
            self.render('payment.html',id=ident,address='')
        else:
            self.redirect(r'/user')
            
class SendHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(r'/main')
        
class ItemHandler(tornado.web.RequestHandler):
    def get(self):
        item = self.application.table('temp').all()
        table = self.application.db
        ident = self.get_argument('id','')
        if ident:
            index = table.get(where('id') == ident)
        else:
            index = {'id':0,'name':'','price':0,'weight':0,'maker':'','category':'',
                     'stock':0,'active':True,'url':'http://'}
        self.render('item.html',item=item,data=table.all(),index=index)
               
class DecideHandler(tornado.web.RequestHandler):
    def post(self):
        s = self.get_argument('post')
        if s == 'second':
            address = self.get_argument('address')
        self.redirect(r'/main')
    
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
    def render(self,id):
        return self.render_string('modules/login.txt',id=id)
    
class Application(tornado.web.Application):
    back = False
    def __init__(self):
        self.ident = {}
        self.db = TinyDB('static/db/db.json')
        handlers =[(r'/main',IndexHandler),(r'/login',LoginHandler),(r'/user',UserHandler),
                   (r'/item',ItemHandler),(r'/cart',CartHandler),(r'/payment',PayHandler),(r'/decide',DecideHandler),
                   (r'/[a-zA-Z0-9]*',SendHandler)]
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
