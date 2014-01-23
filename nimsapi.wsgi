# @author:  Gunnar Schaefer, Kevin S. Hahn

import os
import sys
import site
import ConfigParser

configfile = '../production.ini'
config = ConfigParser.ConfigParser()
config.read(configfile)

site.addsitedir(os.path.join(config.get('nims', 'virtualenv'), 'lib', 'python2.7', 'site-packages'))
sys.path.append(config.get('nims', 'here'))
os.environ['PYTHON_EGG_CACHE'] = config.get('nims', 'python_egg_cache')

import json
import time
import base64
import pymongo
import webapp2
import datetime
import requests
import Crypto.Random
import Crypto.Hash.SHA
import uwsgidecorators
import Crypto.PublicKey.RSA
import Crypto.Signature.PKCS1_v1_5

import logging
import logging.config
logging.config.fileConfig(configfile, disable_existing_loggers=False)
log = logging.getLogger('nimsapi')

import nimsapi
import internimsclient

# read in private key
privkey_file = config.get('nims', 'ssl_key')
try:
    privkey = Crypto.PublicKey.RSA.importKey(open(privkey_file).read())
except:
    log.warn(privkey_file + 'is not a valid private SSL key file')
    privkey = None
else:
    log.info('successfully loaded private SSL key from ' + privkey_file)

# configure uwsgi application
site_id = config.get('nims', 'site_id')
application = nimsapi.app
application.config['stage_path'] = config.get('nims', 'stage_path')
application.config['site_id'] = site_id
application.config['ssl_key']  = privkey

# connect to db
db_uri = config.get('nims', 'db_uri')
application.db = (pymongo.MongoReplicaSetClient(db_uri) if 'replicaSet' in db_uri else pymongo.MongoClient(db_uri)).get_default_database()

# send is-alive signals
api_uri = config.get('nims', 'api_uri')
internims_url = config.get('nims', 'internims_url')

@uwsgidecorators.timer(60)
def internimsclient_timer(signum):
    internimsclient.update(application.db, api_uri, site_id, privkey, internims_url)

@uwsgidecorators.postfork
def random_atfork():
    Crypto.Random.atfork()
