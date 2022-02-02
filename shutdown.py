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
import json, datetime, time, requests
from meraki import DashboardAPI

# Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

# Shut all ports down
def shutdown_ports():
    settings = getJson('settings.json')
    
    m = DashboardAPI(settings['apikey'])

    ports = get_scheduled_ports()
    for s in ports:
        for p in s['ports']:
            for pp in p['ids']:
                url = f"https://api.meraki.com/api/v1/devices/{s['device']}/switch/ports/{pp}"
                headers = {
                    "Content-Type" : "application/json",
                    "Accept" : "application/json",
                    "X-Cisco-Meraki-API-Key" : settings['apikey']
                }
                
                details = m.switch.getDeviceSwitchPort(s['device'], pp)
                details['enabled'] = False

                resp = requests.put(url, headers=headers, json=details)
                resp.raise_for_status()

# Start all ports
def start_ports():
    settings = getJson('settings.json')
    
    m = DashboardAPI(settings['apikey'])

    ports = get_scheduled_ports()
    for s in ports:
        for p in s['ports']:
            for pp in p['ids']:
                url = f"https://api.meraki.com/api/v1/devices/{s['device']}/switch/ports/{pp}"
                headers = {
                    "Content-Type" : "application/json",
                    "Accept" : "application/json",
                    "X-Cisco-Meraki-API-Key" : settings['apikey']
                }
                
                details = m.switch.getDeviceSwitchPort(s['device'], pp)
                details['enabled'] = True

                resp = requests.put(url, headers=headers, json=details)
                resp.raise_for_status()

# Get list of port-scheduled ports
def get_scheduled_ports():
    settings=getJson('settings.json')

    m = DashboardAPI(settings['apikey'])

    result = []
    devices = m.networks.getNetworkDevices(settings['network']['id'])
    for d in devices:
        if 'MS' in d['model']:
            ports = []
            for p in m.switch.getDeviceSwitchPorts(d['serial']):
                if p['portScheduleId'] != None:
                    added = False
                    for p_seen in ports:
                        if (not added) and p['name'] == p_seen['name'] and p['enabled'] == p_seen['enabled'] and p['type'] == p_seen['type'] and p['portScheduleId'] == p_seen['schedule']:
                            p_seen['ids'] += [p['portId']]
                            p_seen['amount'] += 1
                            added = True
                    if not added:
                        ports += [{
                            'name' : p['name'],
                            'ids' : [p['portId']],
                            'enabled' : p['enabled'],
                            'type' : p['type'],
                            'schedule' : p['portScheduleId'],
                            'amount' : 1
                        }]
            result += [{
                'device' : d['serial'],
                'model' : d['model'],
                'ports' : ports
            }]
    
    return result

# Shut down/start up ports if necessary
def check_for_shutdown():
    settings = getJson('settings')

    start = settings['start']
    h_s = int(start[:2])
    m_s = int(start[3:])

    end = settings['end']
    h_e = int(end[:2])
    m_e = int(end[3:])

    h = datetime.datetime.now().hour
    m = datetime.datetime.now().minute

    # After start?
    if h > h_s or (h == h_s and m >= m_s):
        shutdown_ports()
        return
    
    # Before end?
    if h < h_e or (h == h_e and m <= m_e):
        shutdown_ports()
        return
    
    start_ports()

if __name__ == "__main__":
    while True:
        check_for_shutdown()
        # Sleep for 10 minutes
        time.sleep(600)