# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import os
import uuid
import re
import urllib2

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename

from app import app, db, lm #, oid
from config import POSTS_PER_PAGE, UPLOAD_LOCAL_DIR, UPLOAD_PATH, IMAGE_EXT
from forms import LoginForm, PostForm
from models import User, Post, ROLE_USER, ROLE_ADMIN

# logger example
# app.logger.debug('A value for debugging')
# app.logger.warning('A warning occurred (%d apples)', 42)
# app.logger.error('An error occurred')

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def encrypt(data):
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
@login_required
def index(page=1):
    user = g.user
    pagination = Post.query.order_by(Post.sequence).filter_by(user=user).paginate(page, POSTS_PER_PAGE, False)
    posts = pagination.items
    return render_template('index.html', title=u'首页', user=user, posts=posts, pagination=pagination, postform=PostForm())


@app.route('/page/', methods=['POST', 'GET'])
@app.route('/page/<int:post_id>', methods=['POST', 'GET'])
@login_required
def page(post_id=None):
    title = u'新增内容'
    form = PostForm()
    post = None
    # 读取操作
    if request.method == 'GET' and post_id:
        title = u'修改内容'
        post = Post.query.get(post_id)
        form = PostForm(obj=post)
    # 新增、修改操作
    elif request.method == 'POST' and form.validate_on_submit():
        title = u'首页'
        # post = Post(user=g.user, topic=form.topic.data, title=form.title.data, body=form.body.data, sequence=form.sequence.data, timestamp=datetime.utcnow())
        if form.id.data: # 修改
            post = Post.query.get(form.id.data)
            form.populate_obj(post)
        else: # 新增
            form.id.data = None
            post = Post(user=g.user, timestamp=datetime.utcnow())
            form.populate_obj(post)
            db.session.add(post)
        db.session.commit()
        # .paginate(curpage, pagesize, <flag>)
        # flag:错误标记。如果是True,如果接收到超出记录范围的页面请求，那么404错误请求将会自动反馈到客户端浏览器。如果是False，那么一个空列表将会被返回，而不显示错误。
        posts = Post.query.order_by(Post.sequence).filter_by(user=g.user).paginate(1, POSTS_PER_PAGE, False).items
        flash(u'保存成功')
        return redirect(url_for('index'))#render_template('index.html', title=title, posts=posts)
    return render_template('page.html', title=title, post=post, form=form)


@app.route('/remove/<int:post_id>')
@login_required
def remove(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    if request.method == 'POST':
        password = encrypt(request.form['password'])
        user = User.query.filter_by(username=request.form['username'], password=password).first()
        # app.logger.debug(request.form['username'] + ', |' + request.form['password'] + "|")
        if user:
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash(u'用户名或密码错误！')
    form = LoginForm()
    return render_template('login.html',itle=u'登录',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


def allowed_file(filename):
    return True


def listImage(rootDir, retlist):
    for cfile in os.listdir(rootDir):
        path = os.path.join(rootDir, cfile)
        if os.path.isdir(path):
            listImage(path, retlist)
        else:
            ext = cfile.split('.')[-1]
            match = re.search(IMAGE_EXT, ext)
            # if cfile.endswith('.gif') or cfile.endswith('.png') or cfile.endswith('.jpg') or cfile.endswith('.bmp'):
            if match:
                retlist.append(os.path.join(UPLOAD_PATH, g.user.username, 'images', cfile))


@app.route('/s/<path:filepath>')
def getImage(filepath):
    return send_from_directory(UPLOAD_LOCAL_DIR, filepath)


@app.route('/ue/upload/<filetype>', methods=['POST', 'GET'])
@login_required
def imageUpload(filetype='images'):
    if request.method == 'GET' and request.args.get('fetch', None):
        return 'updateSavePath(["s/'+ filetype +'"]);'
    elif request.method == 'POST':
        upfile = request.files['upfile']
        if upfile and allowed_file(upfile.filename):
            filename = ''.join(str(uuid.uuid1()).split('-')) + '.' + secure_filename(upfile.filename).split('.')[-1]
            filetitle = request.form['pictitle']
            filepath = os.path.join(UPLOAD_PATH, str(g.user.username), filetype, filename)
            local_dir = os.path.join(UPLOAD_LOCAL_DIR, str(g.user.username), filetype)
            if not os.path.isdir(local_dir):
                os.makedirs(local_dir)
            upfile.save(os.path.join(local_dir, filename))
            # "{'url':'','title':'','original':'','state':'SUCCESS'}"
            retData = dict(url=filepath, title=filetitle, original=filename, state='SUCCESS')
        # import json
        # app.logger.debug(json.dumps(retData))
        return jsonify(retData)


@app.route('/ue/imageManager', methods=['GET', 'POST'])
@login_required
def imageManager():
    if request.form['action'] == 'get':
        retfiles = []
        listImage(UPLOAD_LOCAL_DIR, retfiles)
        htmlContent = "ue_separate_ue".join(retfiles)
        return htmlContent
    return ""

@app.route('/ue/getRemoteImage', methods=['GET', 'POST'])
@login_required
def getRemoteImage():
    imageUrls = request.form['upfile'].split('ue_separate_ue')
    for iurl in imageUrls:
        ext = iurl.split('.')[-1]
        outUrls = []
        if re.search(IMAGE_EXT, ext):
            filename = ''.join(str(uuid.uuid1()).split('-')) + '.' + ext
            updir = os.path.join(UPLOAD_LOCAL_DIR, g.user.username, 'images')
            if not os.path.isdir(updir):
                os.makedirs(updir)
            with open( os.path.join(updir, filename) , 'wb' ) as upfile:
                upfile.write(urllib2.urlopen(iurl).read())
                outUrls.append(os.path.join(UPLOAD_PATH, 'images', filename))
    outUrls = "ue_separate_ue".join(outUrls)
    return jsonify(url=outUrls, tip=u'远程图片抓取成功！', srcUrl=imageUrls)






