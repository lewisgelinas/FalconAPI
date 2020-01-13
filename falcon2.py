#first request should be to https://api.crowdstrike.com/oauth2/token
#following requests should be made to https://api.crowdstrike.com/"api endpoint" 
 
import urllib
import json
import requests
import datetime
import os


#Side note, these can be exported using envar -- see line #65 
client_id='API Client ID'
client_secret='API Client Secret Key'


class CrowdStrikeDevice:
    def __init__(self, id, json_data):
        self.hostname = json_data['hostname']
        self.device_id= json_data['device_id']
        self.id = id

class CrowdStrikeAPI:
    def __init__(self, client_id, client_secret):
        grant_type='client_credentials'
        auth_url = 'https://api.crowdstrike.com/oauth2/token'
        response = requests.post(auth_url,
            auth=(client_id, client_secret),
                data={'grant_type':grant_type,'client_id':client_id,'client_secret':client_secret})
        tokenJSON = response.json()
        self.token=tokenJSON['access_token']

    def get_devices(self, days_ago=30):
        XdaysAgo= (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
        limitdaysAgo = (datetime.datetime.now() - datetime.timedelta(days=45)).strftime("%Y-%m-%d")
        response= requests.get(
            "https://api.crowdstrike.com/devices/queries/devices/v1?limit=2&filter=last_seen%3A%3E'{}'%2Blast_seen%3A%3C'{}'".format(limitdaysAgo, XdaysAgo), 
                headers={'accept':'application/json', 'Authorization':'Bearer {}'.format(self.token)})

        listData = json.loads(response.text) 
        ids = listData['resources']

        results = []
        for i in ids: 
            response= requests.get(
                "https://api.crowdstrike.com/devices/entities/devices/v1?ids={}".format(i), headers={'accept':'application/json', 'Authorization':'Bearer {}'.format(self.token)})

            listData = json.loads(response.text)
            device = CrowdStrikeDevice(i, listData['resources'][0])
            results.append(device)
            print(i)
        return results


    def remove_devices(self,device):
        postdata= json.dumps({"action_parameters":[{"name":"string","value": "string"}],"ids":["{}".format(device.device_id)]})

        response= requests.post(
            "https://api.crowdstrike.com/devices/entities/devices-actions/v2?action_name=hide_host",  
            headers={'accept':'application/json', 'authorization':'bearer {}'.format(self.token),'Content-Type':'application/json'}, 
            data=postdata)

        if response.status_code == 202:
            print('Successfully deleted ' + device.hostname + " id=" + device.device_id)



#api = CrowdStrikeAPI(os.getenv('CROWD_STRIKE_CLIENT_ID'), os.getenv('CROWD_STRIKE_CLIENT_SECRET'))
api = CrowdStrikeAPI(client_id, client_secret) 

for device in api.get_devices():
    print(device.hostname + " id=" + device.device_id + " is to be deleted")
    #api.remove_devices(device)

    if device.hostname == "ExampleHostName": 
        
        #Uncomment this to remove the hosts
        #api.remove_devices(device)
        
        #---- remove conintue before running ---- 
        continue 
