#!/usr/bin/python
# -*- coding : utf-8 -*-

import gpiozero as gpz
import time
import os.path
import json


startTime = time.time() # Start Zeit des Scripts definieren

ring1ClickCount = 0; # Anzahl erfolgreicher Klingel klicks
ring1StartClick = 0; # Zeit seit letztem klick
ring1Condition = [];
ring1Filename = "ring1Condition.json" # Datei wo der Klingel Algorithmus gespeichert ist
# Datei mit dem Türöffner Algorithmus ainlesen und in einem Array speichern
if(os.path.isfile(ring1Filename)):
    with open(ring1Filename, "r") as read_file:
        ring1Condition = json.load(read_file)
        print("Klingel Algorithmus aus Datei geladen")

doorStatus = False # Definiert ob die Türe offen oder geschlossen ist
doorOpenStart = 0 # Start Zeit der Türöffnung
doorOpenTimeout = 5000 # Zeit in ms wo die Türen offen bleibt

timeToReset = 2000; # Nach dieser Zeit falls keine taste gedrückt wird, wird die Eingabe zurückgesetzt
timeTolerance = 150; # Tolerenz Zeit beim klicken

switchOpener = 1;

def ringHandling():
    if(switchOpener):
        checkOpenerCondition()

def ringSetup():
    global ring1Filename, ring1Condition, button
    print("Start Setup....")
    setupOK = False
    ringSetupStartClick = 0
    ringCondition = []
    ringSetupTime = millis()
    while not setupOK:
        differenceTime = millis() - ringSetupStartClick
        clickCount = 0;
        pullDown = False;
        while((millis() - ringSetupTime) < 5000):
            if(not button.value):
                if(not pullDown):
                    pullDown = True
                    if(clickCount > 0):
                        ringCondition.append(millis() - ringSetupStartClick)
                        clickCount += 1

                    if(clickCount == 0):
                        clickCount = 1

                    ringSetupStartClick = millis()
                    print(clickCount)
            else:
                pullDown = False

        print("----------------------")
        for i in ringCondition:
            print(i)
        print("----------------------")
        query = input('Setup abschliessen [yes/no/cancel]: ')
        Fl = query[0].lower()
        if query == '' or not Fl in ['y','n','c']:
            print('Antworte mit yes oder no!')
        else:
            if Fl == 'y':
                setupOK = True;
                with open(ring1Filename, "w") as write_file:
                    json.dump(ringCondition, write_file)
                ring1Condition = ringCondition
                print("Setup beendet und gespeichert")
            if Fl == 'n':
                ringSetupTime = millis()
                ringCondition = []
                print("Setup erneut gestartet....")
            if Fl == 'c':
                setupOK = True;
                print("Setup abgebrochen")

def doCheckDoorStatus():
    global doorOpenStart, doorStatus, doorOpenTimeout
    difference = millis() - doorOpenStart
    if(doorStatus == True and difference > doorOpenTimeout):
        doorLed.off()
        doorStatus = False
        print("Türe wieder geschlossen")


def resetRing1Trys():
    global ring1ClickCount, ring1StartClick
    ring1ClickCount = 0;
    ring1StartClick = 0;
    print("RESET")

def doDoorOpen():
    global doorStatus, doorOpenStart
    doorStatus = True
    doorLed.on()
    print("Türe offen")
    doorOpenStart = millis()

def millis():
    millis = int(round((time.time() - startTime) * 1000))
    return millis

def checkSingleRing():
    global ring1StartClick, timeToReset
    difference = millis() - ring1StartClick
    if(difference > timeToReset):
        print("Single Ring handle")
        resetRing1Trys()

def checkOpenerCondition():
    global ring1StartClick, ring1Condition, ring1ClickCount, timeTolerance, timeToReset, doorStatus
    differenceTime = millis() - ring1StartClick

    if(differenceTime > timeToReset):
        resetRing1Trys()

    if(doorStatus == False):
        ring1StartClick = millis()
        if(ring1ClickCount > 0 and ring1ClickCount <= len(ring1Condition)):
            if(differenceTime < ring1Condition[ring1ClickCount - 1] + timeTolerance and differenceTime > ring1Condition[ring1ClickCount - 1] - timeTolerance):
                ring1ClickCount += 1;
                if(ring1ClickCount == len(ring1Condition) + 1):
                    doDoorOpen()
                    resetRing1Trys()
            else:
                resetRing1Trys()
        else:
            ring1ClickCount = 1

button = gpz.Button(22) # Aktions Button (multiple use)

ring1 = gpz.Button(24) # Klingel beim Hauseingang
ring1.when_pressed = ringHandling

ring1Reset = gpz.Button(25) # Button für das starten des Setups
ring1Reset.when_pressed = ringSetup

doorLed = gpz.LED(23)

while True:
    doCheckDoorStatus()
