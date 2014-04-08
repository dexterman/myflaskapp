# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = r'\xf11\n\xdb\xb8\x84:\xed\xe2\xbc\x82\x10\xa2\x80g{#u\x03\x87\x18\xb0}\xb0'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# paginate
POSTS_PER_PAGE = 1

UPLOAD_LOCAL_DIR = os.path.join(basedir, 's')
UPLOAD_PATH = os.path.join('/', 's')
