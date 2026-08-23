# P.E.T.E.R v0 ALPHA
#  Program for Electrical Technological Executive Robotics  

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from subprocess import call
import os
import re
import webbrowser
import datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageGrab
import speech_recognition as sr
import pyttsx3
import vlc
import random
import time
from accounts import accountSearch
import pyaudio
import sounddevice as sd
from scipy.io.wavfile import write
from functools import partial

sounds = {}
sites = {"ecosia": "https://ecosia.org/", "google": "https://google.com/", "youtube": "https://youtube.com/"}
increasenumbers = None

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 36.1912,
	"longitude": 44.0094,
	"current": ["temperature_2m", "is_day"],
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_is_day = current.Variables(1).Value()

timerRunning = False
currentTime = 0
startTime = 0
maxTime = 0
latestAppName = None
engine = pyttsx3.init()
r = sr.Recognizer()

class User:
    def __init__(self, hasAccess=False, username="Guest", screenshotLocation="/home/mint/Pictures/", recordingLocation="/home/mint/Recordings"):
        self.username = username
        self.hasAccess = hasAccess
        self.latestScreenshot = None
        self.screenshotLocation = screenshotLocation
        self.timezone = input("What is your timezone?")
        self.userInput = ""
        self.recordingLocation = recordingLocation
    
    def changeAccess(self, bool):
        self.hasAccess = bool

    def changeUsername(self, string):
        self.username = string

mainUser = User()

def TTS(Text):
    engine.say(Text)
    engine.setProperty('rate', 125) 
    engine.runAndWait() 

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def recordAudio():
    recordTime = re.findall(r'\d+', mainUser.userInput)
    if hasNumbers(recordTime):
            fs = 44100  
            seconds = int(recordTime[0])
            print(seconds)
            print(seconds * fs)
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            TTS("Recording audio.")
            sd.wait()  # Wait until recording is finished
            userInput = ""
            write(f'{mainUser.recordingLocation}/Recording {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.wav', fs, recording)
            return True
    else:
        return False

def takeScreenshot():
    mainUser.latestScreenshot = ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay="", window=None, scale_down=False)
    mainUser.latestScreenshot.save(f'{mainUser.screenshotLocation}/{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.png')

def showLatestScreenshot():
    if mainUser.latestScreenshot != None:
        mainUser.latestScreenshot.show()
        return True
    else:
        return False

def getCurrentTime():
    return datetime.datetime.now(ZoneInfo(mainUser.timezone))

def FtC(Number):
    return Number * 9 / 5 + 32
class Commands:
    commandsList = []

    def __init__(self, commandName, commandExecution, commandFunction, commandTrueSpeech, commandFalseSpeech, requiresAccess):
        self.commandName = commandName
        self.commandExecution = commandExecution
        self.commandFunction = commandFunction
        self.commandTrueSpeech = commandTrueSpeech
        self.commandFalseSpeech = commandFalseSpeech
        self.requiresAccess = requiresAccess
        self.commandsList.append(self)

    def executeCommand(self, string):
        if self.commandExecution.lower() in string.lower():
            if (self.requiresAccess == True and mainUser.hasAccess == True) or self.requiresAccess == False:
                
                if self.commandFalseSpeech == "":
                    TTS(self.commandTrueSpeech)
                    self.commandFunction()
                else:
                    commandFunc = self.commandFunction()
                    if commandFunc == True:
                        TTS(self.commandTrueSpeech)
                    elif commandFunc == False:
                        TTS(self.commandFalseSpeech)
                return True
            else:
                TTS("No access.")

class AudioManager(Commands):
    audioDict = {"Loser": "LOSER.mp3", "Thunder": "THUNDER.mp3"}
    commandsDict = None

    def __init__(self, commandSpeech):
        self.player = None
        self.latestAudioName = None
        self.audioLooping = None
        Commands.commandsList.append(self)
        self.commandsDict = {"play": self.playAudioCommand, "stop": self.stopAudio, "repeat": self.repeatAudio, "pause": self.pauseAudio, "resume": self.resumeAudio}
    
    def playAudioCommand(self, string):
        for key, value in self.audioDict.items():
            if key.lower() in string.lower():
                if self.player != None:
                    self.player.stop()
                    self.player = None
                self.latestAudioName = key
                self.player = vlc.MediaPlayer(f"Audio/{value}")
                self.player.play()
                return f"Playing {self.latestAudioName}"
        
    def repeatAudio(self, string):        
        if self.latestAudioName != None:
            self.audioLooping = True
            return f"Repeating {self.latestAudioName}"
        else:
            return f"No audio to repeat."
    
    def stopAudio(self, string):
        if "repeat" in string.lower():
            if self.audioLooping == True:
                self.audioLooping = False
                return "Stopping repeat."
            else:
                return "Audio repeating is not enabled."
        else:
            if self.latestAudioName != None:
                self.latestAudioName = None
                self.player.stop()
                self.player = None
                return f"Stopping audio."
            else:
                return "No audio to stop."

    def pauseAudio(self, string):
        if self.latestAudioName != None:
            self.player.pause()
            return f"Pausing{self.latestAudioName}"
        else:
            return f"No audio to pause."

    def resumeAudio(self, string):
        if self.latestAudioName != None:
            if self.player.get_state() == vlc.State.Paused:
                self.player.play()
                return f"Resuming {self.latestAudioName}"
            else:
                return f"{self.latestAudioName} is {self.player.get_state()}"
        else:
            return f"No audio is playing."

    def executeCommand(self, string):
        for key, value in self.commandsDict.items():
            if key in string.lower():
                    commandExecution = value(string)
                    TTS(commandExecution)
                    return True
            else:
                print("No command")



shutdownCommand = Commands("Shutdown", "shut down", exit, "Shutting down.", "", False)
takeScreenshotCommand = Commands("Take a Screenshot", "Take", takeScreenshot, "Taking a screenshot", "", False)
showLatestScreenshotCommand = Commands("Show latest screenshot", "Show", showLatestScreenshot, "Showing the latest screenshot", "There is no latest screenshot", False)
timeCommand = Commands("Current time", "Time", getCurrentTime, f"The current time is {getCurrentTime().strftime("%I:%M %p")}", "", False)
audioCommands = AudioManager("Playing audio")
recordingCommand = Commands("Record audio", "Record", recordAudio, "Recording has been finished.", "Please determine the length of the recording next time.", False)

TTS("Good day")

while True:
    with sr.Microphone() as source:
        print("Talk")
        audio_text = r.listen(source)
        # recoginze_() method will throw a request
        # error if the API is unreachable,
        # hence using exception handling

    try:
        mainUser.userInput = r.recognize_google(audio_text, language="en-US")
        print("Time over, thanks")
    except sr.UnknownValueError:
        print("Whoops. Some problems on my end")


    if audioCommands.player != None:
        if audioCommands.player.get_state() == vlc.State.Ended:
            if audioCommands.audioLooping == True:
                playAudioFunction = audioCommands.playAudioCommand(audioCommands.latestAudioName)
                print(playAudioFunction)
                print(audioCommands.latestAudioName)
                TTS(playAudioFunction)
            else:
                audioCommands.player = None
                audioCommands.latestAudioName = None

    if mainUser.userInput != "":
        for eachCommand in Commands.commandsList:
            commandExecution = eachCommand.executeCommand(mainUser.userInput)
            userInput = ""
            if commandExecution == True:
                break





# # TTS(f"Good day, {username}")

# while False:


#     if "login" in userInput.lower() and username == "Guest":
#         found, user = accountSearch(userInput)
#         if found:
#             username = user
#             TTS(f"Welcome back, {username}.")
#             HasAccess = True
#             with open("Logs/logins.txt", "a") as f:
#                 f.write(f"Login on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {user} with the following text: {userInput} \n")
#         else:
#             TTS(f"Denied.")
#             with open("Logs/logins.txt", "a") as f:
#                 f.write(f"Denied login on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {username} with the following text: {userInput} \n")

#     # REMINDER: Clean this up. Possibly find a way to loop through all possible numbers between 1-100. 
#     # UPDATE: Should be done
#     if "volume" in userInput.lower():
#         print(re.findall(r'\d+', userInput))
#         increasenumbers = re.findall(r'\d+', userInput)
#         if has_numbers(increasenumbers):
#             call(f'pactl -- set-sink-volume 0 {increasenumbers[0]}% ', shell=True)
#             TTS(f"Volume has been set to {increasenumbers[0]}")
#             increasenumbers = None
#         else:
#             TTS(f"Said message has no numbers.")
    


#         else:
#             TTS(f"Said message has no numbers.")

#     if "open" in userInput.lower():
#             for key, value in sites.items():
#                 if key in userInput.lower():
#                     TTS(f"Opening {key}.")
#                     webbrowser.open(value)

#             # for i in range(len(appnames)):
#             #     if appnames[i] in userInput.lower():
#             #         latestAppName = appnames[i]
#             #         TTS(f"Opening {appnames[i]}.")
#             #         webbrowser.open(appcommands[i])
    
#     if "avengers protocol" in userInput.lower():
#         if HasAccess == True:
#             if p != None:
#                 p.stop()
#             TTS("ASSEMBLE.")
#             latestSongName = "Avengers Protocol"
#             p = vlc.MediaPlayer("Sounds/ASSEMBLE.mp3")
#             p.play()
#         else:
#             TTS(f"Access denied, {username}")
    
#     if "clean up protocol" in userInput.lower():
#         if HasAccess == True:
#             TTS(f"Initiating the clean-up protocol, {username}.")
#             call("killall brave", shell=True)
#             webbrowser.open(sites["ecosia"])
#             webbrowser.open(sites["youtube"])
#             webbrowser.open(sites["reddit"])
#             webbrowser.open(sites["aether"])
#         else:
#             TTS(f"Access denied, {username}")

#     if "beta protocol" in userInput.lower():
#         if HasAccess == True:
#             TTS("Shutting down all systems")
#             call('systemctl poweroff -i', shell=True)

#         else:
#             TTS(f"Access denied, {username}")
    

    

    

    



    

#     # if "timer" in userInput.lower():
#     #     if timerRunning == False:
#     #         timerRunning = True
#     #         startTime = 0
#     #     else:
#     #         TTS(f"A timer is already running, {username}.")

#     # if timerRunning == True:
#     #     currentTime = time.time()
    
#     # if startTime - currentTime >= maxTime:   
#     #     print("yay mario")
#     # NOTE: WORK IN PROGRESS. SEE: TESTSCRIPT.PY
            
#     if "thank" in userInput.lower():
#         TTS(f"At your service, {username}.")
    
#     if "temperature" in userInput.lower():
#         if "fahrenheit" in userInput.lower():
#             TTS(f"The current temperature in fahrenheit is {str(FtC(round(current_temperature_2m)))} degrees.")
#         else:
#             TTS(f"The current temperature is {round(current_temperature_2m)} degrees in celsius.")