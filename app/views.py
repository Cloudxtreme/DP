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

from flask_simplelogin import login_required
import logging

####################
#### blueprints ####
####################

blacklist_blueprint = Blueprint('blacklist', __name__, template_folder='templates')
whitelist_blueprint = Blueprint('whitelist', __name__, template_folder='templates')
policies_blueprint = Blueprint('policies', __name__, template_folder='templates')
ajax_blueprint = Blueprint('ajax', __name__, template_folder='templates')

################
#### config ####
################

app = Flask(__name__)
global VisionIP
#global VisionUser
#global VisionPasswd
VisionIP = "192.168.0.76"
#VisionUser = "radware"
#VisionPasswd = "abc1234..."
logging.basicConfig(filename='app.log',level=logging.WARNING,format='%(asctime)s %(message)s')

###################
#### functions ####
###################

def login():
    import app
    VisionUser = app.VisionUser
    VisionPasswd = app.VisionPasswd
    #Create a session to login
    s = requests.Session()
    loginurl = 'https://'+VisionIP+'/mgmt/system/user/login'
    loginArgs = {'username': VisionUser,'password':VisionPasswd}
    cert = 'APSoluteVisionServer.pem'

    #Try login
    r = s.post(loginurl, verify=False, json=loginArgs)
    r.json()
    return s, VisionUser

def lock(s, device):
    #Lock DefensePro device
    url = 'https://'+VisionIP+'/mgmt/system/config/tree/device/byip/'+device+'/lock'
    r = s.post(url, verify=False)
    r.json()

def unlock(s, device):
    #Unlock DefensePro device
    url = 'https://'+VisionIP+'/mgmt/system/config/tree/device/byip/'+device+'/unlock'
    r = s.post(url, verify=False)
    r.json()

def refresh_policies(s, device):
    url = 'https://'+VisionIP+'/mgmt/device/multi/config/updatepolicies'
    args = {"deviceIpAddresses":[device]}
    r = s.post(url, verify=False, json=args)
    print("POLICIEEEES")
    r.json()

def get_rulesName(s, *device):
    #Get Policies from Device
    device = ''.join(device)
    print(device)
    #Network Protection Policies
    if device:
        url = 'https://'+VisionIP+'/mgmt/device/byip/'+device+'/config/rsIDSNewRulesTable'
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
        url = 'https://'+VisionIP+'/mgmt/device/byip/10.20.30.40/config/rsIDSNewRulesTable'

        r = s.get(url, verify=False)
        data = r.json()
        return ''

def get_DPList(s):
    #Get all DefensePro devices
    url = 'https://'+VisionIP+'/mgmt/system/config/itemlist/alldevices'

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

def delete_BIPs(s, device, banIPs):
    #Delete banIPs
    for banIP in banIPs:
        url = 'https://'+VisionIP+'/mgmt/device/byip/'+device+'/config/rsNewBlackListTable/'+banIP
        r = s.delete(url, verify=False)
        print(url)
        j = r.json()
        print(r.json())


def delete_WIPs(s, device, whiteIP):
    #Delete whiteIPs
    url = 'https://'+VisionIP+'/mgmt/device/byip/'+device+'/config/rsNewWhiteListTable/'+whiteIP
    r = s.delete(url, verify=False)
    print(url)
    j = r.json()
    print(r.json())


def add_IPBlacklist(s, device, banIPs):
    #Add IPs to blacklist
    successMsg = []
    errorMsg = []
    Exception = False
    for banIP in banIPs:
        url = 'https://'+VisionIP+'/mgmt/device/byip/'+device+'/config/rsNewBlackListTable/'+banIP
        args = {
            'rsNewBlackListName': banIP,
            'rsNewBlackListSrcNetwork': banIP,
            'rsNewBlackListDstNetwork': 'any',
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
        j = r.json()
        print(r.json())
        if "Exception" in j:
            Exception = True
            print("Erroooooooooor")
            print(j['message'])
            errorMsg.append(j['message'] + " [" + banIP + "]")
            if j['message'] == "M_00386: An entry with same key already exists.":
                print("Ya existe")
            elif j['message'] == "M_00386: Entry already exists in White list.":
                print("Ya existe")
            else:
                delete_BIPs(s, device, banIP)
        else:
            successMsg.append(banIP)

    return [errorMsg], [successMsg]

def add_IPWhitelist(s, device, whiteIPs):
    #Add IPs to whitelist
    successMsg = []
    errorMsg = []
    Exception = False
    for whiteIP in whiteIPs:
        url = 'https://'+VisionIP+'/mgmt/device/byip/'+device+'/config/rsNewWhiteListTable/'+whiteIP
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
        j = r.json()
        print(r.json())
        if "Exception" in j:
            Exception = True
            print("Erroooooooooor")
            print(j['message'])
            errorMsg.append(j['message'] + " [" + whiteIP + "]")
            if j['message'] == "M_00386: An entry with same key already exists.":
                print("Ya existe")
            elif j['message'] == "M_00386: Entry already exists in Black list.":
                print("Ya existe")
            else:
                delete_WIPs(s, device, whiteIP)

        else:
            successMsg.append(whiteIP)

    return [errorMsg], [successMsg]

def update_Policies(s, enablePolicies):
    #Modify rule action

    #Report Only ~ rsIDSNewRulesAction: 0
    #Block and Report ~ rsIDSNewRulesAction: 1
    for rule, enable in enablePolicies:
        url = 'https://'+VisionIP+'/mgmt/device/byip/192.168.0.11/config/rsIDSNewRulesTable/'+rule
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

	url = 'https://'+VisionIP+'/mgmt/device/byip/192.168.0.11/config/rsIDSNewRulesTable'

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
	s, VisionUser = login()
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

@blacklist_blueprint.route('/blacklist', methods=['GET', 'POST'])
@login_required
def banlist():
    s, VisionUser = login()
    error = ""
    success = ""

    if request.method == 'POST':
        device = request.form['device']
#        refresh_policies(s, device)
        lock(s, device)

        if request.form['banIPs']:
            banIPs = request.form['banIPs']
            banIPs = banIPs.split(",")
            error, success = add_IPBlacklist(s, device, banIPs)

        refresh_policies(s, device)
        unlock(s, device)
        logging.warning('%s added the following IPs to the BlackList: %s', VisionUser, success)
    DPName, DPIP = get_DPList(s)
    DPDevices = zip(DPName, DPIP)
    return render_template('blacklist.html', DPDevices=DPDevices, error=error, success=success, VisionUser=VisionUser)

@whitelist_blueprint.route('/whitelist', methods=['GET', 'POST'])
@login_required
def whitelist():
    s, VisionUser = login()
    error = ""
    success = ""

    if request.method == 'POST':
        device = request.form['device']
#        refresh_policies(s, device)
        lock(s, device)

        if request.form['whiteIPs']:
            whiteIPs = request.form['whiteIPs']
            whiteIPs = whiteIPs.split(",")
            error, success = add_IPWhitelist(s, device, whiteIPs)

        refresh_policies(s, device)
        unlock(s, device)
        logging.warning('%s added the following IPs to the WhiteList: %s', VisionUser, success)
    DPName, DPIP = get_DPList(s)
    DPDevices = zip(DPName, DPIP)
    return render_template('whitelist.html', DPDevices=DPDevices, error=error, success=success, VisionUser=VisionUser)

@policies_blueprint.route('/policies', methods=['GET', 'POST'])
@login_required
def policies(*RulesName, **RulesAction):
    s, VisionUser = login()
    DPName, DPIP = get_DPList(s)
    DPDevices = zip(DPName, DPIP)

    if request.method == 'POST':
        device = request.form['device']
        RulesName = get_rulesName(s, device)
        RulesAction = get_policyAction(s, device)
        # Save old policies (Policies before changed)
        oldEnablePolicies = zip(RulesName, RulesAction)
        old = list(zip(oldEnablePolicies))

        # Save new policies
        enables = request.form.getlist('enables[]')
        enablePolicies = zip(RulesName, enables)
        # I don't know why is necessary create another var..
        enablePolicies2 = zip(RulesName, enables)
        new = list(zip(enablePolicies2))

        lock(s, device)
        time.sleep(1)
        update_Policies(s, enablePolicies)
        time.sleep(1)
        unlock(s, device)
        refresh_policies(s, device)

        # Log changed policies     
        # Compare two zips and get the changed value
        oldynew = zip(old, new)
        oldynew = [x1 if x1!=x2 else '' for x1, x2 in oldynew]

        # Remove white values..
        for x in oldynew:
            if x!= '':
                oldynew = x

        oldynew = ''.join(str(e) for e in oldynew)

        #Report Only ~ rsIDSNewRulesAction: 0
        #Block and Report ~ rsIDSNewRulesAction: 1
        logging.warning('%s changed the following policies: %s', VisionUser, oldynew)
        return redirect('/policies')

    return render_template('policies.html', DPDevices=DPDevices, VisionUser=VisionUser)

