""" Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

# Import Section
from email import header
from wsgiref.util import request_uri
from flask import Flask, render_template, request, url_for, redirect
from collections import defaultdict
import datetime
import requests
import json
from dotenv import load_dotenv
import os, csv
from meraki import DashboardAPI
from dnacentersdk import api

# load all environment variables
load_dotenv()


# Global variables
app = Flask(__name__)


#Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

#Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)
    f.close()


##Routes
#Instructions

#Index
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        settings = getJson("settings.json")
        network_ids = dict(request.form.lists())['network']
        print(network_ids)
        m = DashboardAPI(settings['apikey'])
        networks = []
        for id in network_ids:
            n = {
                    "name" : m.networks.getNetwork(id)['name'],
                    "id" : id,
                }
            networks += [n]
        settings['networks'] = networks
        writeJson("settings.json", settings)
    
    settings = getJson("settings.json")
    m = DashboardAPI(api_key=settings['apikey'])
    try:
        ports = get_scheduled_ports()
        return render_template('home.html', devices=ports, now=settings['start'], later=settings['stop'])
    except Exception as e:
        print(e)
        return render_template('home.html')

#Settings
@app.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        apikey = request.form.get('apikey')
        settings = getJson("settings.json")
        settings['apikey'] = apikey
        writeJson("settings.json", settings)

        m = DashboardAPI(apikey)
        networks = []
        for o in m.organizations.getOrganizations():
            for n in m.organizations.getOrganizationNetworks(o['id']):
                networks += [{"org" : o['name'], "name": n['name'], "id":n['id']}]
        return render_template('settings.html', hiddenLinks=True, settings=getJson("settings.json"), apikeyset=True, networks=networks)

    try:
        #Page without error message and defined header links 
        return render_template('settings.html', hiddenLinks=True, settings=getJson("settings.json"), apikeyset=False, networks=[])
    except Exception as e: 
        print(e)  
        #OR the following to show error message 
        return render_template('settings.html', hiddenLinks=True)

#Schedule
@app.route('/schedule', methods=["GET", "POST"])
def schedule():
    if request.method == "POST":
        settings=getJson('settings.json')
        start = request.form.get('start')
        stop = request.form.get('stop')
        settings['start'] = start
        settings['stop'] = stop
        writeJson('settings.json', settings)

        ports = dict(request.form.lists())['port']
        result = []
        for p in ports:
                splitted = p.split('.')
                serial = splitted[0]
                port = splitted[1]
                result += [[serial, port]]
        writeJson('scheduled_ports.json', result)

    return redirect(request.referrer)

## Helper functions
def get_scheduled_ports():
    settings=getJson('settings.json')

    m = DashboardAPI(settings['apikey'])

    result = []
    devices = []
    for n_id in settings['networks']:
        try:
            devices += m.networks.getNetworkDevices(n_id['id'])
        except:
            print('Failed to get device')
    for d in devices:
        if 'MS' in d['model']:
            ports = []
            for p in m.switch.getDeviceSwitchPorts(d['serial']):
                # added = False
                # for p_seen in ports:
                #     # if (not added) and p['name'] == p_seen['name'] and p['enabled'] == p_seen['enabled'] and p['type'] == p_seen['type'] and p['portScheduleId'] == p_seen['schedule']:
                #     #     p_seen['ids'] += [p['portId']]
                #     #     p_seen['amount'] += 1
                #     #     added = True

                # if not added:
                ports += [{
                    'name' : p['name'],
                    'id' : p['portId'],
                    'enabled' : p['enabled'],
                    'type' : p['type'],
                    'schedule' : p['portScheduleId'],
                    'checked' : True
                }]
            result += [{
                'device' : d['serial'],
                'model' : d['model'],
                'ports' : ports
            }]
    
    with open('ports.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    return getJson('ports.json')   

@app.route('/portlist', methods=["GET"])
def show_from_csv():
    result = []
    with open('uploaded.csv', 'r') as f:
        settings=getJson('settings.json')
        reader = csv.reader(f)
        serial_seen = {}

        for line in reader:
            serial = line[0]
            port = line[1]
            if serial not in serial_seen:
                serial_seen[serial] = [port]
            else:
                serial_seen[serial] += [port]

        m = DashboardAPI(settings['apikey'])
        for serial in serial_seen:
            try:
                ports = []
                for p in m.switch.getDeviceSwitchPorts(serial):
                    checked = False
                    if p['portId'] in serial_seen[serial]:
                        checked=True
                    ports += [{
                        'name' : p['name'],
                        'id' : p['portId'],
                        'enabled' : p['enabled'],
                        'type' : p['type'],
                        'schedule' : p['portScheduleId'],
                        'checked' : checked
                    }]
                device = m.devices.getDevice(serial)
                result += [{
                    'device' : device['serial'],
                    'model' : device['model'],
                    'ports' : ports
                }]
            except:
                print('Wrong serial number')
        
        with open('ports.json', 'w') as f:
            json.dump(result, f, indent=2)  

        return render_template('home.html', devices=result, now=settings['start'], later=settings['stop'])

@app.route("/extract-api-keys", methods=["GET","POST"])
def upload_file_function():
    uploaded_file = request.files
    file_dict = uploaded_file.to_dict()
    the_file = file_dict["file"]
    if not the_file.filename.lower().endswith('.csv'):
        return "Please upload a valid CSV format, or enter the API keys manually"
    with open('uploaded.csv', 'wb') as f:
        f.write(the_file.read())
    
    return "Read CSV file"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999, debug=True)