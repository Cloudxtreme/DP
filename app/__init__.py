# -*- encoding: utf-8 -*-
"""
Autor: alexfrancow
"""

#################
#### imports ####
#################

from flask import Flask
from flask_simplelogin import SimpleLogin
import requests

################
#### config ####
################

app = Flask(__name__, instance_relative_config=True)

def visionLogin(user):
    """:param user: dict {'username': 'foo', 'password': 'bar'}"""
    username = user.get('username')
    password = user.get('password')
    VisionIP = "192.168.0.76"

    s = requests.Session()
    loginurl = 'https://'+VisionIP+'/mgmt/system/user/login'
    loginArgs = {'username': username,'password':password}
    r = s.post(loginurl, verify=False, json=loginArgs)
    response = r.json()
    print(response)
    if 'Exception' in response:
    #if user.get('username') == 'chuck' and user.get('password') == 'norris':
       return False
    return True

SimpleLogin(app, login_checker=visionLogin)


####################
#### blueprints ####
####################

from app.views import blacklist_blueprint, policies_blueprint, ajax_blueprint, whitelist_blueprint

# register the blueprints
app.register_blueprint(blacklist_blueprint)
app.register_blueprint(policies_blueprint)
app.register_blueprint(ajax_blueprint)
app.register_blueprint(whitelist_blueprint)
