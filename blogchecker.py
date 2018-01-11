#!/usr/bin/env python

import urllib.request
import json
from dateutil import parser
import time
import os
import valve.source.a2s

SERVER = "163.172.17.175"
PORT = 30616

pipe_path = "/tmp/pipe2bot"

servercache = "/tmp/rustsrvcache"

sleeptime = 30

apiurl = "https://api.facepunch.com/api/public/manifest/?public_key=j0VF6sNnzn9rwt9qTZtI02zTYK8PRdN1"

#Usage: player_list((SERVER, PORT))
def serverinfo(server):
    result = None
    while result is None:
        try:
            serverdict = {}

            server = valve.source.a2s.ServerQuerier(server)
            players = server.players()
            if len(players) > 0:
                playernamelist = []
                playertimelist = []
                for player in players["players"]:
                    playernamelist.append(player["name"])
                    playertimelist.append(player["duration"])
                serverdict["playernames"] = playernamelist
                serverdict["playertimes"] = playertimelist
            serverdict["num_players"], serverdict["max_players"], serverdict["server_name"], serverdict["version"] = \
            server.info()["player_count"], \
            server.info()["max_players"], \
            server.info()["server_name"], \
            server.info()["version"]
            serverdict["ping"] = round(server.ping())
            result = serverdict
        except Exception as e:
            print(e)
            time.sleep(10)
            pass
    with open(servercache, 'w') as file:
        file.write(json.dumps(result))



# They have two ways of defining Date and Content. Both are accounted for.

def extracttime(item):
    try:
        return parser.parse(item["Date"])
    except:
        return parser.parse(item["DateTime"])


def extractcontent(item):
    try:
        return "{} - {}".format(item["Title"], item["Url"])
    except:
        return item["Content"]


def mostRecentItem():
    # Loading from json facepunch api
    urlresult = urllib.request.urlopen(apiurl)
    jsonOutput = json.loads(urlresult.read().decode("utf-8"))["News"]

    # Defining lists needed
    datetimelist = []
    contentlist = []

    for item in jsonOutput:
        for item2 in jsonOutput[item]:
            datetimelist.append(extracttime(item2))
            contentlist.append(extractcontent(item2))
    fulldict = (dict(zip(datetimelist, contentlist)))

    return sorted(fulldict.items(), key=lambda p: p[0], reverse=True)[0][1]

def toPipe(data):
    pipeout = os.open(pipe_path, os.O_WRONLY)
    os.write(pipeout, "{}\n".format(data).encode())

if not os.path.exists(pipe_path):
    os.mkfifo(pipe_path)

lastPost = mostRecentItem()
print("Startup: {}".format(lastPost))

time.sleep(10)

while True:
    success = False
    while not success:
        success = True
        try:
            loopLastPost = mostRecentItem()
        except:
            success = False
            time.sleep(sleeptime)

    if loopLastPost != lastPost:
        toPipe(mostRecentItem())
    serverinfo((SERVER, PORT))
    time.sleep(sleeptime)