#!/usr/bin/env python
#
# @author:  Gunnar Schaefer

import os
import sys
import site

site.addsitedir('/var/local/webapp2/lib/python2.7/site-packages')
sys.path.append('/var/local/post')
os.environ['PYTHON_EGG_CACHE'] = '/tmp/python_egg_cache'


import pymongo
import webapp2
import nimsapi
import nimsutil

logfile = '/var/local/log/nimsapi.log'
db_uri = 'mongodb://nims:cnimr750@cnifs.stanford.edu,cnibk.stanford.edu/nims?replicaSet=cni'
stage_path = '/scratch/upload'

nimsutil.configure_log(logfile, False)
db_client = pymongo.MongoReplicaSetClient(db_uri) if 'replicaSet' in db_uri else pymongo.MongoClient(db_uri)

application = nimsapi.app
application.config = dict(stage_path=stage_path))
application.db = db_client.get_default_database()
