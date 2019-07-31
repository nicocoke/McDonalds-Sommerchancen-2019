import json
import uuid
import requests
import subprocess
import sys
from time import sleep

print (""" 
 ____________________________
|                            |
| CREDIT WHERE CREDIT'S DUE: |
|                            |
|   CREATOR: Cronick         |
|   WEB: Ash                 |
|____________________________|

   _____ _          _ _                                   
  / ____| |        | | |                                  
 | (___ | |__   ___| | |___  ___  ___       _ ____      __
  \___ \| '_ \ / _ \ | / __|/ _ \/ __|     | '_ \ \ /\ / /
  ____) | | | |  __/ | \__ \  __/ (__   _  | |_) \ V  V / 
 |_____/|_| |_|\___|_|_|___/\___|\___| (_) | .__/ \_/\_/  
                                           | |            
                                           |_|                              
""")
sys.stdout.flush()
sleep(1)

# Generate vmob uid & Plexure API Key
vmob_uid = str(uuid.uuid4()).upper()
plexure_api_key = subprocess.Popen(["java", "plexure", vmob_uid], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").replace("\n","")

username = sys.argv[1]
password = sys.argv[2]
offerId = sys.argv[3]

def obfuscate(str):
    first = str[0:6]
    last = str[len(str)-6:len(str)-1]
    return first + "************************" + last

print("[#] vmob_uid: " + obfuscate(vmob_uid))
sys.stdout.flush()
sleep(0.5)
print("[#] plexure_api_key: " + obfuscate(plexure_api_key))
print("")
sys.stdout.flush()
sleep(1)

# Endpoints
URL_LOGIN = "https://con-west-europe-gma.vmobapps.com/v3/logins"
URL_POINTS = "https://con-west-europe-gma.vmobapps.com/v3/consumers/points"
URL_OFFERACTIVATION = "https://con-west-europe-gma.vmobapps.com/v3/consumers/loyaltyCardInstances/{instanceId}/offeractivation"

# Headers
HEADERS_LOGIN = {
    'Accept-Language': 'da-DK',
    'Content-Type': 'application/json',
    'x-plexure-api-key': plexure_api_key,
    'x-vmob-application_version': '3118',
    'x-vmob-device': 'iPhone',
    'x-vmob-device_network_type': 'wifi',
    'x-vmob-device_os_version': '12.2',
    'x-vmob-device_screen_resolution': '1334x750',
    'x-vmob-device_type': 'i_p',
    'x-vmob-device_utc_offset': '+02:00',
    'x-vmob-uid': vmob_uid
}

# Parameters
PARAMS_LOGIN = {'password':str(password),'username':str(username),'returnConsumerInfo':'true','returnCrossReferences':'false','grant_type':'password'}
PARAMS_POINTS = {'loyaltyCardId':571,'pointsRequested':1,'autoActivateReward':'false','fillMultipleCards':'true','transactionId':'Campaign_Activation:'+str(uuid.uuid4()).upper()}
PARAMS_OFFERACTIVATION = {'offerId':int(offerId)}

# Login to the user and retrieve BEARER access token
R_LOGIN = requests.post(url=URL_LOGIN, headers=HEADERS_LOGIN, json=PARAMS_LOGIN) 
JSON_LOGIN = json.loads(R_LOGIN.text)

if(R_LOGIN.status_code == 200):
    access_token = "bearer " + R_LOGIN.json()['access_token']
    print("[#] Login OK - Access Token: ", obfuscate(access_token))
    sys.stdout.flush()
    sleep(1)
else:
    print("Error while getting bearer! Error code " + str(R_LOGIN.status_code))
    sys.stdout.flush()
    sleep(0.5)
    print(R_LOGIN.content.decode())
    sys.stdout.flush()
    sleep(1)

# Add point to obtain a coupon
if(R_LOGIN.status_code == 200):
    HEADERS_POINTS = {
        'Accept-Language': 'da-DK',
        'Authorization': access_token,
        'Content-Type': 'application/json',
        'x-plexure-api-key': plexure_api_key,
        'x-vmob-application_version': '3118',
        'x-vmob-device': 'iPhone',
        'x-vmob-device_network_type': 'wifi',
        'x-vmob-device_os_version': '12.2',
        'x-vmob-device_screen_resolution': '1334x750',
        'x-vmob-device_type': 'i_p',
        'x-vmob-device_utc_offset': '+02:00',
        'x-vmob-uid': vmob_uid
    }
    PARAMS_POINTS = {'loyaltyCardId':571,'pointsRequested':1,'autoActivateReward':'false','fillMultipleCards':'true','transactionId':'Campaign_Activation:'+str(uuid.uuid4()).upper()}

    R_POINTS = requests.post(url=URL_POINTS, headers=HEADERS_POINTS, json=PARAMS_POINTS)

    if(R_POINTS.status_code == 201):
        instanceId = R_POINTS.json()['pointCreationSummary'][0]['instanceId']
        print("[#] Point for coupon added! - instanceId: ", obfuscate(instanceId))
        sys.stdout.flush()
        sleep(1)
    else:
        print("[#] Unable to add point for coupon - Have you redeemed too many today?")
        sys.stdout.flush()
        sleep(1)

    # Adding your coupon
    if(R_POINTS.status_code == 201):
        R_OFFERACTIVATION = requests.post(url=URL_OFFERACTIVATION.replace("{instanceId}", instanceId), headers=HEADERS_POINTS, json=PARAMS_OFFERACTIVATION)
        if(R_POINTS.status_code == 201):
            print("[#] Coupon added! Enjoy")
            sys.stdout.flush()
        else:
            print("[#] Something failed!")
            sys.stdout.flush()
