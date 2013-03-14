#!/usr/bin/env python
# -*- coding: utf-8 -*-

## ------------------------------------------ ##

import sqlite3, mailer
from hashlib import md5

class User(object):

    def __init__(self):
        
        pass

    def create(self): # create table if not exists
        # user accont info
        self.cur.execute('''CREATE TABLE if not exists user (uid INTEGER PRIMARY KEY, username text, password text, utype text, SignupDate datetime)''')
        # user activation info
        self.cur.execute('''CREATE TABLE if not exists activation (uid INTEGER, code text, status boolean)''');

        # user query log
        self.cur.execute('''CREATE TABLE if not exists query (uid INTEGER, query text, time datetime)''')
        # user activity log
        self.cur.execute('''CREATE TABLE if not exists login (uid INTEGER, time datetime)''')


    def connect(self, dbname):
        self.con = sqlite3.connect(dbname)
        self.cur = self.con.cursor()

        ### check if table exist, maybe delete this function after online
        self.create()

    def info(self, username, password, utype):
        self.username = username.strip()
        self.rawpassword = password
        self.password = md5(password).hexdigest()
        self.utype = utype.strip()

    def exist(self):
        # check if user exist
        self.cur.execute('''SELECT * FROM user WHERE username = ? and utype = ?''', (self.username, self.utype) )
        return True if self.cur.fetchone() else False

    def matched(self):
        # check count & password correctness
        self.cur.execute('''SELECT * FROM user WHERE username = ? and password = ? and utype = ? ''', (self.username, self.password, self.utype) )

        return True if self.cur.fetchone() else False
      
    def login_log(self):

        # self.cur.execute('''SELECT uid from user where username = ? and utype = ?''', (self.username, self.utype))
        # uid = self.cur.fetchone()[0]

        uid = self.get_uid(self.username, self.utype)
        self.cur.execute('''INSERT into login values (?, datetime('now','localtime'))''', (uid, ))
        self.con.commit()

    def query_log(self, query, uid):

        # self.cur.execute('''SELECT uid from user where username = ? and utype = ?''', (self.username, self.utype))
        # uid = self.cur.fetchone()[0]

        # uid = self.get_uid(self.username, self.utype)
        self.cur.execute('''INSERT into query values (?, ?, datetime('now','localtime'))''', (uid, query))
        self.con.commit()


    # def get_uid(self):
        # return self.uid

    # def get_utype(self):
        # return self.utype

    ## for signup
    def add(self):

        try:
            # [table: user], insert a new user data
            self.cur.execute("insert into user values (?, ?, ?, ?, datetime('now','localtime'))", (None, self.username, self.password, self.utype))

            # [table: user], fetch uid of current user
            self.cur.execute('''SELECT uid FROM user WHERE username = ? and password = ? and utype = ? ''', (self.username, self.password, self.utype) )
            uid = self.cur.fetchone()[0]

            # generate activation code and set default activation status
            ActivationCode = md5(''.join([self.username, self.password, self.utype])).hexdigest()
            ActivationStatus = False
            

            # [table: activation]
            self.cur.execute("insert into activation values (?, ?, ?)", (uid, ActivationCode, ActivationStatus))

            
            add_success = True
        except:
            add_success = False

        if add_success:
            if self.utype == 'email':

                url = 'http://linggle.com/signup?u='+str(uid)+'&'+'c='+str(ActivationCode)

                html = '<html>'
                html += '<head></head>'
                html += '<body>'
                html += '<br>'
                html += 'Hi, <br>'
                html += '<p>'
                html += 'These are your account information<br>'
                html += '<blockquote>'
                html += 'Your email: <a href="mailto:%s">%s</a>' % (self.username, self.username)
                html += '<br>'
                html += 'Your Password: %s ' % (self.rawpassword)
                html += '</blockquote>'
                html += '</p>'
                html += '<p>'
                html += 'Please visit <a href="%s" target="_black">this link</a> to activate your account.' % (url)

                html += '<hr><br>'
                html += 'or copy the link below and paste in your browser to activate manully'
                html += '<blockquote>'
                html += url
                html += '</blockquote>'
                html += '<br><hr>'
                html += '</p>'
                html += '<p>'
                html += 'Have fun :P'
                html += '</p>'
                html += '</body>'


                m = mailer.Mailer()
                m.Server('Gmail', 587) # server , port

                m.To(self.username)
                m.From('maxis1718@gmail.com')

                m.Auth('maxis1718', 'seefish1030')

                m.Content(html, 'html')
                m.Subject('Hi, Linggler!')

                m.send(True)
                
            else:
                ## facebook or gmail, set validation to "True"
                self.cur.execute("UPDATE activation SET status = ? WHERE uid = ?", (True, uid))
                
        self.con.commit()
        return add_success

    def getInfo(self, uid):
        info = {}

        self.cur.execute('''select u.username, a.status from user as u, activation as a where u.uid == a.uid and u.uid = 1''')
        (info['username'], info['activation']) = self.cur.fetchone()
        return info

    def getAcvtivation(self, username):
        self.cur.execute('''select u.username, a.status from user as u, activation as a where u.uid == a.uid and u.uid = 1''')
        print self.cur.fetchone()

        self.cur.execute('''select a.status from activation as a, user as u where u.uid == a.uid and u.username == ?''', (username, ))
        return self.cur.fetchone()[0]

    def get_uid(self, username, utype):
        self.cur.execute('''SELECT uid from user where username = ? and utype = ?''', (self.username, self.utype))
        return self.cur.fetchone()[0]

    def setActive(self, uid, code):
        self.cur.execute("UPDATE activation SET status = ? WHERE uid = ? and code = ?", (True, uid, code))
        self.con.commit()

    def close(self):
        self.cur.close()
        self.con.close()

## ------------------------------------------ ##

## 之後底下這些 function 全部砍掉，改寫成從外部宣告 class之後直接用!!!

# def getUserInfo():


def querylog(query, uid):
    user = User()
    user.connect('databases/user.db3')
    user.query_log(query, uid)
    user.close()

def active(request):
    user = User()
    user.connect('databases/user.db3')
    uid, code = request.args.get('u'), request.args.get('c')
    user.setActive(uid, code)
    user.close()

def getUserInfoByID(request):
    user = User()
    user.connect('databases/user.db3')
    uid = request.args.get('u')
    info = user.getInfo(uid)
    user.close()
    return info

# def getUserInfoByName(request):
def getAcvtivation(request):
    user = User()
    user.connect('databases/user.db3')
    # 
    info = user.getAcvtivation(request.form['username'])
    user.close()
    return info


def login(request):

    status = {}

    user = User()
    user.connect('databases/user.db3')
    user.info(request.form['username'], request.form['password'], request.form['utype'])

    if user.exist(): # user already exist
        if user.matched():

            # log the login event
            user.login_log()

            status['type'] = 'success' 
            status['msg'] = 'Login Successfully.'
            status['uid'] = user.get_uid(request.form['username'], request.form['utype'])
            # status['utype'] = request.form['utype']

        else:
            status['type'] = 'incorrect_password'
            status['msg'] = 'Please check your <red>password</red>.'
    else: # user should signup first
        status['type'] = 'user_not_exist'
        status['msg'] = 'Please check your <red>Email Address</red>. <br>or  Not a lingger? Just <red>signup</red>!'

    user.close()

    return status
    
def signup(request):

    status = {}

    user = User()
    user.connect('databases/user.db3')
    user.info(request.form['username'], request.form['password'], request.form['utype'])

    # 'User already exists. Please check your email address or contact the developers.'
    if user.exist():
        status['type'] = 'user_already_exist' 
        status['msg'] = 'User already <red>exists.</red>'
    else:
        if user.add():
            status['type'] = 'success'
            status['msg'] = 'Signup successfully.<br>Please check your email for account activation.'
        else:
            status['type'] = 'server_failed'
            status['msg'] = '<red>Database error</red>, please contact the developers.'
    user.close()

    return status


if __name__ == '__main__':
    # getUserInfo(1)
    getAcvtivation('maxis1718@gmail.com')
    # getUserInfoByName('vincent732@gmail.com')
