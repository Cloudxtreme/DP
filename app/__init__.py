# -*- encoding: utf-8 -*-
"""
Autor: alexfrancow
"""

#################
#### imports ####
#################

from flask import Flask

################
#### config ####
################

app = Flask(__name__, instance_relative_config=True)


####################
#### blueprints ####
####################

from app.views import login_blueprint, banlist_blueprint, policies_blueprint

# register the blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(banlist_blueprint)
app.register_blueprint(policies_blueprint)
