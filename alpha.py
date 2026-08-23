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

p = None
timerRunning = False
currentTime = 0
startTime = 0
maxTime = 0
latestSongName = None
latestAppName = None
loopSong = False
engine = pyttsx3.init()
IsTalking = True;
r = sr.Recognizer()

class User:
    def __init__(self, hasAccess=False, username="Guest", screenshotLocation="/home/mint/Pictures/"):
        self.username = username
        self.hasAccess = hasAccess
        self.latestScreenshot = None
        self.screenshotLocation = screenshotLocation
    
    def changeAccess(self, bool):
        self.hasAccess = bool

    def changeUsername(self, string):
        self.username = string

mainUser = User()

def TTS(Text):
    engine.say(Text)
    engine.setProperty('rate', 125) 
    engine.runAndWait() 

def takeScreenshot():
    latestScreenshot = ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay="", window=None, scale_down=False)
    latestScreenshot.save(f'{mainUser.screenshotLocation}/{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.png')

def FtC(Number):
    return Number * 9 / 5 + 32

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

class Commands:
    commandsList = []

    def __init__(self, commandName, commandExecution, commandFunction, commandSpeech, requiresAccess):
        self.commandName = commandName
        self.commandExecution = commandExecution
        self.commandFunction = commandFunction
        self.commandSpeech = commandSpeech
        self.requiresAccess = requiresAccess
        self.commandsList.append(self)

    def executeCommand(self, string):
        if self.commandExecution.lower() in string.lower():
            if (self.requiresAccess == True and mainUser.hasAccess == True) or self.requiresAccess == False:
                TTS(self.commandSpeech)
                self.commandFunction()
            else:
                TTS("No access.")
        else:
            print("No command")

shutdownCommand = Commands("Shutdown", "shut down", exit, "Shutting down.", False)
takeScreenshotCommand = Commands("Take a Screenshot", "Take Screenshot", takeScreenshot, "Taking a screenshot", False)


TTS("Good day")

while True == True: 
    user_input = ""

    with sr.Microphone() as source:
        print("Talk")
        audio_text = r.listen(source)
        # recoginze_() method will throw a request
        # error if the API is unreachable,
        # hence using exception handling
    
    try:
        user_input = r.recognize_google(audio_text, language="en-US")
        print("Time over, thanks")
    except sr.UnknownValueError:
        print("Whoops. Some problems on my end")

    if user_input != "":
        for eachCommand in Commands.commandsList:
            eachCommand.executeCommand(user_input)





# # TTS(f"Good day, {username}")

# while False:


#     if "login" in user_input.lower() and username == "Guest":
#         found, user = accountSearch(user_input)
#         if found:
#             username = user
#             TTS(f"Welcome back, {username}.")
#             HasAccess = True
#             with open("Logs/logins.txt", "a") as f:
#                 f.write(f"Login on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {user} with the following text: {user_input} \n")
#         else:
#             TTS(f"Denied.")
#             with open("Logs/logins.txt", "a") as f:
#                 f.write(f"Denied login on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by {username} with the following text: {user_input} \n")

#     if "shutdown" in user_input.lower() or "disable" in user_input.lower() or "cut" in user_input.lower():
#         TTS(f"Shutting down, {username}")
#         exit()
    
#     # Use a list of possible greetings from me for this
#     if "hello" in user_input.lower() or "peter" in user_input.lower():
#         TTS(greetings[random.randint(0, 4)])
    
#     if "time" in user_input.lower():
#         time = datetime.datetime.now(ZoneInfo("Asia/Baghdad"))
#         print(f"The current time is {time.strftime("%I:%M %p")}")
#         TTS(f"The current time is {time.strftime("%I:%M %p")}")

#     # REMINDER: Clean this up. Possibly find a way to loop through all possible numbers between 1-100. 
#     # UPDATE: Should be done
#     if "volume" in user_input.lower():
#         print(re.findall(r'\d+', user_input))
#         increasenumbers = re.findall(r'\d+', user_input)
#         if has_numbers(increasenumbers):
#             call(f'pactl -- set-sink-volume 0 {increasenumbers[0]}% ', shell=True)
#             TTS(f"Volume has been set to {increasenumbers[0]}")
#             increasenumbers = None
#         else:
#             TTS(f"Said message has no numbers.")
    
#     if "record" in user_input.lower():
#         recordTime = re.findall(r'\d+', user_input)
#         if has_numbers(recordTime):
#             TTS(f"Recording for {recordTime}")
#             fs = 44100  
#             seconds = int(recordTime[0])
#             print(seconds)
#             print(seconds * fs)
#             myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
#             sd.wait()  # Wait until recording is finished
#             write(f'Recording {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.wav', fs, myrecording)  # Save as WAV file 

#         else:
#             TTS(f"Said message has no numbers.")

#     if "open" in user_input.lower():
#             for key, value in sites.items():
#                 if key in user_input.lower():
#                     TTS(f"Opening {key}.")
#                     webbrowser.open(value)

#             # for i in range(len(appnames)):
#             #     if appnames[i] in user_input.lower():
#             #         latestAppName = appnames[i]
#             #         TTS(f"Opening {appnames[i]}.")
#             #         webbrowser.open(appcommands[i])
    
#     if "avengers protocol" in user_input.lower():
#         if HasAccess == True:
#             if p != None:
#                 p.stop()
#             TTS("ASSEMBLE.")
#             latestSongName = "Avengers Protocol"
#             p = vlc.MediaPlayer("Sounds/ASSEMBLE.mp3")
#             p.play()
#         else:
#             TTS(f"Access denied, {username}")
    
#     if "clean up protocol" in user_input.lower():
#         if HasAccess == True:
#             TTS(f"Initiating the clean-up protocol, {username}.")
#             call("killall brave", shell=True)
#             webbrowser.open(sites["ecosia"])
#             webbrowser.open(sites["youtube"])
#             webbrowser.open(sites["reddit"])
#             webbrowser.open(sites["aether"])
#         else:
#             TTS(f"Access denied, {username}")

#     if "beta protocol" in user_input.lower():
#         if HasAccess == True:
#             TTS("Shutting down all systems")
#             call('systemctl poweroff -i', shell=True)

#         else:
#             TTS(f"Access denied, {username}")
    

    
#     if "loop sound" in user_input.lower():
#         if latestSongName != None:
#             TTS(f"Looping {latestSongName}")
#             loopSong = True
#         else:
#             TTS("No song to loop.")

#     if loopSong == True:
#         current_state = p.get_state()
#         print(f"LOOP LOOP 000: {current_state}")
#         if current_state == vlc.State.Ended:
#             p = vlc.MediaPlayer(f"Sounds/{sounds.get(latestSongName)}")
#             p.play()
    
#     if "play" in user_input.lower():
#             for key, value in sounds.items():
#                 if key in user_input.lower():
#                     if p != None:
#                         p.stop()
#                         p = None
#                     latestSongName = key
#                     TTS(f"Playing {key}.")
#                     p = vlc.MediaPlayer(f"Sounds/{value}")
#                     p.play() 
#             #     elif songnames[i] == songnames[-1]:
#             #         TTS(f"No such song found, {username}.")
#                 # NOTE: REIMPLEMENT ABOVE ^
    
#     if "stop" in user_input.lower():
#         if "loop" in user_input.lower():
#             if loopSong == True:
#                 loopSong = False
#                 TTS("Stopping loop.")
#             else:
#                 TTS("Looping is not on.")
#         else:
#             if latestSongName != None:
#                 TTS(f"Stopping {latestSongName}")
#                 latestSongName = None
#                 p.stop()
#             else:
#                 TTS(f"No song is playing, {username}")

#     if "pause" in user_input.lower():
#         if latestSongName!= None:
#             if p.get_state() == vlc.State.Playing:
#                 p.pause()
#                 TTS(f"Pausing {latestSongName}.")
#         else:
#             TTS(f"No song to pause, {username}.")

#     if "unpause" in user_input.lower() or "resume" in user_input.lower():
#         if latestSongName != None:
#             if p.get_state() == vlc.State.Paused:
#                 p.play()
#                 TTS(f"Resuming {latestSongName}")
#             else:
#                 TTS(f"{latestSongName} is {p.get_state()}")
#         else:
#             TTS(f"No song is playing, {username}.")
    
#     if latestSongName != None:
#         if p.get_state() == vlc.State.Ended:
#             p = None
#             latestSongName = None

#     # if "timer" in user_input.lower():
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

    
#     if "screenshot" in user_input.lower():
#         if "take" in user_input.lower():
#             latestImage = ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay="", window=None, scale_down=False)
#             latestImage.save(f'/home/mint/Pictures/{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.png')
#             TTS(f"A screenshot has been taken, {username}.")
#         elif "show" in user_input.lower():
#             if latestImage != None:
#                 latestImage.show()
#                 TTS(f"Showing latest screenshot, {username}.")
#             else:
#                 TTS(f"No latest screenshot, {username}.")
            
#     if "thank" in user_input.lower():
#         TTS(f"At your service, {username}.")
    
#     if "temperature" in user_input.lower():
#         if "fahrenheit" in user_input.lower():
#             TTS(f"The current temperature in fahrenheit is {str(FtC(round(current_temperature_2m)))} degrees.")
#         else:
#             TTS(f"The current temperature is {round(current_temperature_2m)} degrees in celsius.")