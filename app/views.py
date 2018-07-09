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
import subprocess
import time
import json
import pprint

import requests
from requests import Request, Session

####################
#### blueprints ####
####################

login_blueprint = Blueprint('login', __name__, template_folder='templates')
banlist_blueprint = Blueprint('banlist', __name__, template_folder='templates')
policies_blueprint = Blueprint('policies', __name__, template_folder='templates')
ajax_blueprint = Blueprint('ajax', __name__, template_folder='templates')

################
#### config ####
################

app = Flask(__name__)

###################
#### functions ####
###################

def login():
    #Create a session to login
    s = requests.Session()
    loginurl = 'https://192.168.0.76/mgmt/system/user/login'
    loginArgs = {'username':'radware','password':'abc1234.'}
    cert = 'APSoluteVisionServer.pem'

    #Try login
    r = s.post(loginurl, verify=False, json=loginArgs)
    r.json()
    return s

def get_rulesName(s, *device):
    #Get Policies from Device
    device = ''.join(device)
    print(device)
    #Network Protection Policies
    if device:
        url = 'https://192.168.0.76/mgmt/device/byip/'+device+'/config/rsIDSNewRulesTable'
        r = s.get(url, verify=False)
        data = r.json()

    #Modify the response manual
        data = data['rsIDSNewRulesTable']
        RulesName = []
        for d in data:
            for k, v in d.items():
                if k == 'rsIDSNewRulesName':
                    RulesName.append(v)
        return RulesName

    else:
        url = 'https://192.168.0.76/mgmt/device/byip/10.20.30.40/config/rsIDSNewRulesTable'

        r = s.get(url, verify=False)
        data = r.json()
        return ''

def get_DPList(s):
    url = 'https://192.168.0.76/mgmt/system/config/itemlist/alldevices'

    r = s.get(url, verify=False)
    data = r.json()

    #Modify the response
    DPName = []
    DPIP = []
    for d in data:
        for k, v in d.items():
            if k == 'name':
                DPName.append(v)
            if k == 'managementIp':
                DPIP.append(v)
    return DPName, DPIP

def add_IPBlacklist(s, device, banIPs):
    for banIP in banIPs:
        url = 'https://192.168.0.76/mgmt/device/byip/'+device+'/config/rsNewBlackListTable/'+banIP
        args = {
            'rsNewBlackListName': banIP,
            'rsNewBlackListSrcNetwork': banIP,
            'rsNewBlackListDstNetwork': banIP,
            'rsNewBlackListSrcPortGroup': '',
            'rsNewBlackListDstPortGroup': '',
            'rsNewBlackListPhysicalPort': '',
            'rsNewBlackListVLANTag': '',
            'rsNewBlackListProtocol': '0',
            'rsNewBlackListState': '1',
            'rsNewBlackListDirection': '1',
            'rsNewBlackListAction': '1',
            'rsNewBlackListReportAction': '0',
            'rsNewBlackListDescription': banIP,
            'rsNewBlackListExpirationHour': '0',
            'rsNewBlackListExpirationMinute': '0',
            'rsNewBlackListOriginatedIP': '0.0.0.0',
            'rsNewBlackListOriginatedModule': '0',
            'rsNewBlackListDetectorSecurityModule': '0',
            'rsNewBlackListDynamicState': '2',
            'rsNewBlackListPacketReport': '2'
        }

        r = s.post(url, verify=False, json=args)
        print(url)
        r.json()
        print(r.json())

def add_IPWhitelist(s, device, whiteIPs):
    for whiteIP in whiteIPs:
        url = 'https://192.168.0.76/mgmt/device/byip/'+device+'/config/rsNewWhiteListTable/'+whiteIP
        args = {
            'rsNewWhiteListName': whiteIP,
            'rsNewWhiteListSrcNetwork': whiteIP,
            'rsNewWhiteListDstNetwork': whiteIP,
            'rsNewWhiteListSrcPortGroup': '',
            'rsNewWhiteListDstPortGroup': '',
            'rsNewWhiteListPhysicalPort': '',
            'rsNewWhiteListVLANTag': '',
            'rsNewWhiteListProtocol': '0',
            'rsNewWhiteListState': '1',
            'rsNewWhiteListDirection': '1',
            'rsNewWhiteListAction': '0',
            'rsNewWhiteListReportAction': '0',
            'rsNewWhiteListDescription': whiteIP,
            'rsNewWhiteListAllModules': '1',
            'rsNewWhiteListSynModule': '1',
            'rsNewWhiteListStatefulModule': '1',
            'rsNewWhiteListScanningModule': '1',
            'rsNewWhiteListSignatureModule': '1',
            'rsNewWhiteListHttpFloodModule': '1',
            'rsNewWhiteListServerCrackingModule': '1'
        }

        r = s.post(url, verify=False, json=args)
        print(url)
        r.json()
        print(r.json())

def update_Policies(s, enablePolicies):
    #Report Only ~ rsIDSNewRulesAction: 0
    #Block and Report ~ rsIDSNewRulesAction: 1
    for rule, enable in enablePolicies:
        url = 'https://192.168.0.76/mgmt/device/byip/192.168.0.11/config/rsIDSNewRulesTable/'+rule
        print(rule)
        print(enable)
        if '0' in enable:
            args = {'rsIDSNewRulesAction':'0'}
            r = s.put(url, verify=False, json=args)
            r.json()

        elif '1' in enable:
            args = {'rsIDSNewRulesAction':'1'}
            r = s.put(url, verify=False, json=args)
            r.json()


def get_policyAction(s, *device):
	#Report Only ~ rsIDSNewRulesAction: 0
	#Block and Report ~ rsIDSNewRulesAction: 1

	url = 'https://192.168.0.76/mgmt/device/byip/192.168.0.11/config/rsIDSNewRulesTable'

	r = s.get(url, verify=False)
	data = r.json()

	#Modify the response manual
	data = data['rsIDSNewRulesTable']
	policyAction = []
	for d in data:
    		for k, v in d.items():
        		if k == 'rsIDSNewRulesAction':
            			policyAction.append(v)
	return policyAction


################
####  AJAX  ####
################

@ajax_blueprint.route('/_select_DP', methods=['GET'])
def select_DP():
	s = login()
	device = request.args.get('a')
	# Get Rules from device
	RulesName = get_rulesName(s, device)
	print(RulesName)

	# Get RulesAction from device
	RulesAction = get_policyAction(s, device)
	print(RulesAction)

	# Two lists to json
	JSONRules = json.dumps(
		[{'RuleName':name, 'RuleXAction':action} for name, action in zip(RulesName, RulesAction)], sort_keys=True
	)
	#JSONRules = [{'RuleName':name, 'RuleAction':action} for name, action in zip(RulesName, RulesAction)]
	print("=============")
	print(JSONRules)

	return jsonify(JSONRules=JSONRules)


################
#### routes ####
################

@login_blueprint.route('/', methods=['GET', 'POST'])
def main():
    return render_template('banlist.html')


@banlist_blueprint.route('/banlist', methods=['GET', 'POST'])
def banlist():
    s = login()

    if request.method == 'POST':
        device = request.form['device']
        print(device)

        if request.form['banIPs']:
            banIPs = request.form['banIPs']
            banIPs = banIPs.split(",")
            print(banIPs)
            add_IPBlacklist(s, device, banIPs)

        if request.form['whiteIPs']:
            whiteIPs = request.form['whiteIPs']
            whiteIPs = whiteIPs.split(",")
            add_IPWhitelist(s, device, whiteIPs)

    DPName, DPIP = get_DPList(s)
    # https://stackoverflow.com/questions/17139807/jinja2-multiple-variables-in-same-for-loop
    DPDevices = zip(DPName, DPIP)

    return render_template('banlist.html', DPDevices=DPDevices)


@policies_blueprint.route('/policies', methods=['GET', 'POST'])
def policies(*RulesName, **RulesAction):
    s = login()

    # Get all devices list (name + ip)
    DPName, DPIP = get_DPList(s)
    DPDevices = zip(DPName, DPIP)

    if request.method == 'POST':
        device = request.form['device']
        print(device)
        RulesName = get_rulesName(s, device)
        enables = request.form.getlist('enables[]')
        print(enables)
        enablePolicies = zip(RulesName, enables)
        update_Policies(s, enablePolicies)
        time.sleep(1)
        return redirect('/policies')

    return render_template('policies.html', DPDevices=DPDevices)
