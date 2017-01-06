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
        user = self.application.ident
        table = self.application.db.table('item')
        if user:
            ident = user['name']
        else:
            ident = 'guest'
        s = self.get_argument('search','')
        if s:
            data = table.search(where('name') == s)
        else:
            detail = self.get_argument('detail','')
            if detail:
                data = table.search(where('name') == detail)
                self.render('modules/main2.html',items=self.items(),new=self.new(),cart=self.cart(),id=ident,number=3,data=data)
                return
            data = table.all()
        self.render('modules/main.html',items=self.items(),new=self.new(),cart=self.cart(),id=ident,number=5,data=data)
         
    def items(self):
        for x in self.application.db.table('item').all():
            yield x['category']
            
    def cart(self):
        s = {}
        table = self.application.db.table('item')
        for x in self.application.db.table('cart').all():
            item = table.get(where('item_id') == x['item_id'])
            s[item['name']] = item['price']
        return s
    
    def new(self):
        table = self.application.db.table('item')
        for x in self.application.db.table('new').all():
            item = table.get(where('item_id') == x['item_id'])
            yield item['name']
              
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
                table.insert({'ident':user['ident'],'item_id':ident,'count':count})
        else:
            table.insert({'ident':0,'item_id':ident,'count':count})
        self.redirect(r'/main')
                
class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        ident = self.get_argument('id','')
        if ident:
            self.application.db.remove(where('id') == ident)
              
class PayHandler(tornado.web.RequestHandler):
    def get(self):
        ident = self.application.ident
        if ident:
            self.render('payment.html',id=ident)
        else:
            self.application.back = True
            self.redirect(r'/user')
            
class SendHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect(r'/main')
        
class ItemHandler(tornado.web.RequestHandler):
    index = {'item_id':0,'name':'','price':0,'weight':0,'category':'',
            'stock':0,'active':True,'url':'http://'}    

    def get(self):
        self.read()
        ident = self.get_argument('id','')
        if ident:
            q = (where('ident') == self.application.ident['ident'])&(where('item_id') == int(ident))
            self.index = self.application.db.table('temp').search(q)
        else:
            self.index['maker'] = self.application.ident['name']
        self.render('item.html',item=self.item,data=self.table,index=self.index)
          
    def post(self):
        self.read()
        self.index['ident'] = self.application.ident['ident']
        self.index['item_id'] = self.get_argument('id','')
        self.index['name'] = self.get_argument('name','')
        self.index['price'] = self.get_argument('price',0)
        self.index['weight'] = self.get_argument('weight',0)
        self.index['maker'] = self.application.ident['name']
        self.application.db.table('temp').insert(self.index)
        self.render('item.html',item=self.item,data=self.table,index=self.index)
        
    def read(self):
        q = where('ident') == self.application.ident['ident']
        self.item = self.application.db.table('temp').search(q)
        self.table = self.application.db.table('item').search(q)
                     
class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        item,mode = self.any()
        self.render('admin.html',item=item,mode=mode)
    
    def post(self):
        ident = self.get_argument('id')
        table = self.application.db.table('temp')
        el = table.get(where('item_id') == ident)
        if el:
            self.application.db.table('item').insert(el)
            table.remove(eids=[el.eid])
        item,mode = self.any()            
        self.render('admin.html',item=item,mode=mode)
        
    def any(self):
        mode = self.get_argument('mode','const')
        code = 'checked=check'
        if mode == 'const':
            item = self.application.db.table('temp').all()
            s = [code,'','']
        elif mode == 'open':
            item = self.application.db.table('item').search(where('active') == True)
            s = ['','',code]
        else:
            item = self.application.db.table('item').search(where('active') == False)
            s = ['',code,'']
        return item,s
        
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
                   (r'/admin',AdminHandler),(r'/[a-zA-Z0-9]*',SendHandler)]
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
