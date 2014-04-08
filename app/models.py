# -*- coding: utf-8 -*-
from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    gid = db.Column(db.Integer)#, nullable=False)
    username = db.Column(db.String(60))#, nullable=False)
    password = db.Column(db.String(32))#, nullable=False)
    email = db.Column(db.String(90))#, nullable=False)
    createtime = db.Column(db.String(13))#, nullable=False)
    lasttime = db.Column(db.String(13))#, nullable=False)
    status = db.Column(db.String(1))#, nullable=False)
    createip = db.Column(db.String(30))#, nullable=False)
    lastip = db.Column(db.String(30))#, nullable=False)
    diynum = db.Column(db.Integer)#, nullable=False)
    activitynum = db.Column(db.Integer)#, nullable=False)
    card_num = db.Column(db.Integer)#, nullable=False)
    card_create_status = db.Column(db.SmallInteger)#, nullable=False)
    wechar_card_num = db.Column(db.SmallInteger)#, nullable=False)
    money = db.Column(db.Integer)#, nullable=False)
    viptime = db.Column(db.String(13))#, nullable=False)
    connectnum = db.Column(db.Integer)#, nullable=False)
    lastloginmonth = db.Column(db.SmallInteger)#, nullable=False)

    posts = db.relationship('Post', backref = 'user', lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.String(90), nullable=False)
    title = db.Column(db.String(90))
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sequence = db.Column(db.Integer, server_default='0')
    status = db.Column(db.String(10), server_default='0')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.topic)
