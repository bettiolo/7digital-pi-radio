#!/usr/bin/env python

import os
import sys
import time
import mpd
import json
import urllib.request
import pifacecad#_emulator as pifacecad

GRACENOTE_USER_ID = os.environ.get('GRACENOTE_USER_ID')

client = mpd.MPDClient()
cad = pifacecad.PiFaceCAD()
baseUrl = "http://radio-7g.herokuapp.com/api/"
currentTrackIndex = 0


def initializeButtons():
    listener = pifacecad.SwitchEventListener()
    for pstation in range(8):
        listener.register(pstation, pifacecad.IODIR_ON, buttonPressed)
    listener.activate()


def buttonPressed(event):
    global currentTrackIndex
    print(event.pin_num)
    if event.pin_num == 3:
        play(currentTrackIndex + 1)


def initializeLcd():
    # cad.lcd.backlight_off()
    # cad.lcd.backlight_on()
    cad.lcd.blink_off()
    cad.lcd.cursor_off()
    cad.lcd.clear()
    cad.lcd.write("Initializing ...")


def initializeMpdClient():
    client.connect("localhost", 6600)
    # print(client.decoders())
    # print(client.urlhandlers())
    client.stop()
    client.clear()
    client.single(1)


def getPlaylist():
    radioCreateUrl = baseUrl + "radio/create?artistName=Calvin+Harris&gnUserId=" + GRACENOTE_USER_ID
    print("Loading radio tracks: " + radioCreateUrl)
    return json.loads(urllib.request.urlopen(radioCreateUrl).read().decode())


def getTrackId(trackIndex):
    return playlist['tracks'][trackIndex]['sevendigitalId']


def getArtistName(trackIndex):
    return playlist['tracks'][trackIndex]['artist']


def getTrackTitle(trackIndex):
    return playlist['tracks'][trackIndex]['title']


def getStreamUrl(trackId):
    streamUrl = baseUrl + "stream/" + str(trackId)
    print("Loading stream: " + streamUrl)
    return json.loads(urllib.request.urlopen(streamUrl).read().decode())['mp3Url']


def play(trackIndex):
    global currentTrackIndex
    currentTrackIndex = trackIndex
    streamUrl = getStreamUrl(getTrackId(currentTrackIndex))
    client.stop()
    client.clear()
    print("Streaming: " + streamUrl)
    client.add(streamUrl)
    # client.seek(0, 0)
    # client.seekcur(0)
    artist = getArtistName(currentTrackIndex)
    title = getTrackTitle(currentTrackIndex)
    track = artist + " - " + title

    print("Playing: " + track)
    client.play()
    cad.lcd.clear()
    cad.lcd.write(artist[:16])
    cad.lcd.write("\n")
    cad.lcd.write(title[:16])


initializeButtons()
initializeLcd()
initializeMpdClient()
playlist = getPlaylist()

play(0)

try:
    while True:
        # print(client.status())
        time.sleep(1)
except:
    # print("Unexpected error:", sys.exc_info()[0])
    print('Stopping')
    cad.lcd.clear()
    client.stop()
    client.close()
    client.disconnect()
