
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG

import requests

__author__ = "Julia Albert"

# Funktion zur Formulierung des Requests (LED-Namen und Aktionsbezeichnung anpassen)
def makeRequest(led, action):


    if led =="tinted red":
        led = "bred"
    elif led =="tinted green":
        led = "bgreen"

    if action == "on":
        action = "ON"
    elif action == "off":
        action == "OFF"


    return led, action

# Extrafunktion die alle LEDs "gleichzeitig" bedienen kann
def allLED(action):
    urlRed = "http://192.168.178.29/rest/items/red"
    urlGreen = "http://192.168.178.29/rest/items/green"
    urlBgreen = "http://192.168.178.29/rest/items/bgreen"
    urlBred = "http://192.168.178.29/rest/items/bred"

    try:
        responseRed = requests.post(urlRed, data=action)
        print(responseRed)

        responseGreen = requests.post(urlGreen, data=action)
        print(responseGreen)

        responseBgreen = requests.post(urlBgreen, data=action)
        print(responseBgreen)

        responseBred = requests.post(urlBred, data=action)
        print(responseBred)

    except KeyError:
        pass

    return responseRed, responseGreen, responseBred, responseBgreen

# Funktion, die Request zusammensetzt und absendet
def requestNormal(led, action):
        url = "http://192.168.178.29/rest/items/" + led

        try:
            response = requests.post(url, data=action)
        except KeyError:
            pass

        return response


# Skillklasse
class ArduinoLEDControlSkill(MycroftSkill):

    # Konstruktor
    def __init__(self):
        super(ArduinoLEDControlSkill, self).__init__(name="ArduinoLEDControlSkill")

    # Intents definieren
    def initialize(self):

        # Intent on/off
        on_off_intent = IntentBuilder("On_Off_Intent").require("action").require("ledName").require("actionName").build()
        self.register_intent(on_off_intent, self.handle_on_off_intent)

        #Intent dimmer
        brightness_value_intent = IntentBuilder("Brightness_Value_Intent").require("action").require("ledName").require("brightnessValue").build()
        self.register_intent(brightness_value_intent, self.handle_brightness_value_intent)

    # Intent-handler für An- oder Ausschalten defininieren
    def handle_on_off_intent(self, message):

        # Variablen an Unserinput (Spracheingabe) anpassen
        ledMessage = message.data.get("ledName")
        actionMessage = message.data.get("actionName")

        # Request formulieren
        led, action = makeRequest(ledMessage, actionMessage)

        # Request(s) senden und Sprachausgabe machen
        if led == "all":
            resRed, resGreen, resBred, resBgreen = allLED(action)
            if resRed.status_code == 200 and resGreen.status_code == 200 and resBred.status_code == 200 and resBgreen.status_code == 200:
                self.speak_dialog("allOnOff", {"name": ledMessage, "status": actionMessage})
            else:
                self.speak_dialog("request.fail")
        else:
            res = requestNormal(led, action)
            if res.status_code == 200:
                self.speak_dialog("OnOff", {"name": ledMessage, "status": actionMessage})
            else:
                self.speak_dialog("request.fail")

    # Intent-handler für bestimmte Helligkeitswerte (Vorgehensweise s.o.)
    def handle_brightness_value_intent(self, message):

        ledMessage = message.data.get("ledName")
        valueMessage = message.data.get("brightnessValue")

        led, action = makeRequest(ledMessage, valueMessage)

        if led == "all":
            resRed, resGreen, resBred, resBgreen = allLED(action)
            if resRed.status_code == 200 and resGreen.status_code == 200 and resBred.status_code == 200 and resBgreen.status_code == 200:
                self.speak_dialog("allDim", {"name": ledMessage, "status": valueMessage})
            else:
                self.speak_dialog("request.fail")
        else:
            res = requestNormal(led, action)
            if res.status_code == 200:
                self.speak_dialog("Dim", {"name": ledMessage, "status": valueMessage})
            else:
                self.speak_dialog("request.fail")

    # Ausführung bei Stop-Intent (hier keine Funktion)
    def stop(self):
        pass

# Skill erstellen
def create_skill():
    return ArduinoLEDControlSkill()
