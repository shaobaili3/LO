#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import io
import sys
import urllib.request
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
print('utf8 string test: ', '卡尼能布恩', '째남모')
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    "https://1138a186a6384b00a20a6196273c3009@o958702.ingest.sentry.io/5907306",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

from os import error, name
from flask import Flask, jsonify
import json
from Models import master
from flask.json import tag
from Models import player
from Models.setting import Server
from Models.player import Player
from Models.network import Network
from Models.riot import Riot
from Models.local import Local
from Models.setting import Setting
from Models.leaderboard import checkRank, updateLeaderboard
import time
import threading
from Models.process import updateTrackServer

settingInspect = Setting()
networkInspect = Network(settingInspect)
riotInspect = Riot(networkInspect)
playerInspect = Player(riotInspect)
localInspect = Local(settingInspect)

settingTrack = Setting()
networkTrack = Network(settingTrack)
riotTrack = Riot(networkTrack)
playerTrack = Player(riotTrack)
localTrack= Local(settingTrack)


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self.processWork()
        self.leaderboardsWork()

    def processWork(self):
        def run_work():
            while True:
                updateTrackServer(settingTrack)
                time.sleep(2)
        work = threading.Thread(target=run_work)
        work.start()

    def leaderboardsWork(self):
        def run_work():
            while True:
                updateLeaderboard()
                time.sleep(600)
        work = threading.Thread(target=run_work)
        work.start()

app = FlaskApp(__name__)

@app.route("/process", methods = ['get'])
def process():
    process_info = {}
    process_info['server'] = settingTrack.riotServer
    process_info['port'] = settingTrack.port
    return jsonify(process_info)

@app.route("/track", methods = ['get'])
def track():
    settingTrack.setServer(Server._value2member_map_[settingTrack.riotServer])
    return jsonify(localInspect.updateStatusFlask())

@app.route("/history/<string:server>/<string:name>/<string:tag>", methods = ['get'])
def history(server, name, tag):
    if server == 'sea':
        print('history: Riot API not suppport SEA')
        return jsonify([])
    settingInspect.setServer(Server._value2member_map_[server])
    playerInspect.inspectFlask(name, tag)
    playerInspect.loadMatchsToFlask()
    return jsonify(playerInspect.historyFlask.__dict__['history'])

@app.route("/name/<string:server>/<string:playername>", methods = ['get'])
def get_names(server, playername):
    settingInspect.setServer(Server._value2member_map_[server])
    localInspect.updatePlayernames()
    playerList = set()
    for name in localInspect.playernames:
        if name[0:len(playername)].lower() == playername.lower():
            playerList.add(name)

    returnList = jsonify(list(playerList))
    return returnList

@app.route("/inspect/<string:server>/<string:name>/<string:tag>", methods = ['get'])
def inspect(name, tag, server):
    settingInspect.setServer(Server._value2member_map_[server])
    playerInspect.inspectFlask(name, tag)
    inspection = {} 
    inspection['history'] = playerInspect.historyFlask.__dict__['history']
    inspection['matches'] = playerInspect.matchesJson
    return jsonify(inspection)


@app.route("/search/<string:server>/<string:name>/<string:tag>", methods = ['get'])
def search(name, tag, server):
    print('search#######################server: ', server)
    settingInspect.setServer(Server._value2member_map_[server])
    playerInspect.inspectFlask(name, tag)
    inspection = {} 
    inspection['history'] = playerInspect.historyFlask.__dict__['history']
    inspection['matches'] = playerInspect.matchesJson
    return jsonify(playerInspect.matchesJson)

app.run(port=63312)

