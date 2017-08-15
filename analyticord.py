import requests
import threading
checkForUpdates = True
noMessages = False
version = 1.0
verifiedMessages = True
messages = 0
token = 0

server = "http://analyticord.solutions"
def init(tokenB):
    global token
    token = tokenB
    r = requests.get(server + "/api/botLogin",  headers={'Authorization': 'bot ' + str(token)})
    data = r.json()
    if data.get('error'):
        print("[AC] Login failed. Your bot will continue to start, but not send data to Analyticord.")
    else:
        if noMessages == False: print("[AC] Logged in to Analyticord as " + data['name'])
        
    if checkForUpdates:
        r = requests.get(server + "/api/version?lib=python",  headers={'Authorization': 'bot srOQXHXBW2TSMzhj2OMtuL3gXZiSppvZm7CIRImUjGAm6Q2K91Z5XrtMF5YEXawT0zQzVggmcvLFUmYzleRkymNStJWVHPvelKCArEZA4cIwWDBXIkaaotxSYz3QUplR'})
        body = r.text
        if float(body) > version:
            print("[AC] Version " + str(body) + " is avaliable, you're running " + str(version) + " update to use that latest features. https://github.com/analyticord/module-python")
    
def send(eventType, data):
    r = requests.post(server + "/api/submit", data={'eventType': eventType, 'data': data},  headers={'Authorization': 'bot srOQXHXBW2TSMzhj2OMtuL3gXZiSppvZm7CIRImUjGAm6Q2K91Z5XrtMF5YEXawT0zQzVggmcvLFUmYzleRkymNStJWVHPvelKCArEZA4cIwWDBXIkaaotxSYz3QUplR'})
    body = r.json()
    if body.get('error'):
        print("[AC] Failed to send data, " + eventType + "/" + data)
    else:
        if verifiedMessages:
            print("[AC] Success! The data was sent! Verify that it's the correct information at: https://analyticord.solutions/api/verified?id=" + body['ID'])

def message():
    global messages
    messages = messages + 1

def submitMessages():
    global token
    global messages
    threading.Timer(60.0, submitMessages).start() 
    if messages > 0:
        r = requests.post(server + "/api/submit", data={'eventType': "messages", 'data': messages},  headers={'Authorization': 'bot ' + token})
        body = r.json()
        if body.get('error'):
            print("[AC] Something went wrong while trying to send data.")
        else:
            messages = 0
            if verifiedMessages:
                print("[AC] Success! The data was sent! Verify that it's the correct information at: https://analyticord.solutions/api/verified?id=" + body['ID'])
                
submitMessages()
