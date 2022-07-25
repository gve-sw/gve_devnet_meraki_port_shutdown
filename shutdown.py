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

def shutdown_ports():
    print('Starting up all ports...')
    settings = getJson('settings.json')
    
    m = DashboardAPI(settings['apikey'])

    ports = getJson('scheduled_ports.json')
    for p in ports:
        url = f"https://api.meraki.com/api/v1/devices/{p[0]}/switch/ports/{p[1]}"
        headers = {
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            "X-Cisco-Meraki-API-Key" : settings['apikey']
        }
            
        details = m.switch.getDeviceSwitchPort(p[0], p[1])
        details['enabled'] = False

        resp = requests.put(url, headers=headers, json=details)
        resp.raise_for_status()
    print('Done')

def start_ports():
    print('Starting up all ports...')
    settings = getJson('settings.json')
    
    m = DashboardAPI(settings['apikey'])

    ports = getJson('scheduled_ports.json')
    for p in ports:
        url = f"https://api.meraki.com/api/v1/devices/{p[0]}/switch/ports/{p[1]}"
        headers = {
            "Content-Type" : "application/json",
            "Accept" : "application/json",
            "X-Cisco-Meraki-API-Key" : settings['apikey']
        }
            
        details = m.switch.getDeviceSwitchPort(p[0], p[1])
        details['enabled'] = True

        resp = requests.put(url, headers=headers, json=details)
        resp.raise_for_status()
    print('Done')

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
        time.sleep(600)