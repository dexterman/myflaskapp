# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, PasswordField, IntegerField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length

class LoginForm(Form):
    username = TextField(u'用户名', validators = [InputRequired(u'必填'), Length(min=3, max=10, message=u'请输入大于%(min)d, 小于%(max)d个字符！')])
    password = PasswordField(u'密码', validators = [InputRequired(u'必填'), Length(min=1, max=16, message=u'请输入大于%(min)d, 小于%(max)d个字符！')])
    # remember_me = BooleanField('remember_me', default = False)

class PostForm(Form):
    id = HiddenField(u'编号')
    topic = TextField(u'Tab标题', validators = [InputRequired(u'必填'), Length(max=10, message=u'请输入小于%(max)d个中文字符！')])
    title = TextField(u'标题')
    sequence = IntegerField(u'排序')
    body = TextAreaField(u'内容')
