# P.E.T.E.R v0 ALPHA

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
import timeManager 

sites = {"ecosia": "https://ecosia.org/", "google": "https://google.com/", "youtube": "https://youtube.com/"}

timerRunning = False
currentTime = 0
startTime = 0
maxTime = 0
latestAppName = None
engine = pyttsx3.init()
r = sr.Recognizer()

class User:
    def __init__(self, hasAccess=False, username="Guest", screenshotLocation="/home/mint/Pictures/", recordingLocation="/home/mint/Recordings", audioLocation="home/mint/Music"):
        self.username = username
        self.hasAccess = hasAccess
        self.latestScreenshot = None
        self.screenshotLocation = screenshotLocation
        self.timezone = input("What is your timezone?")
        self.userInput = ""
        self.recordingLocation = recordingLocation
        self.audioLocation = audioLocation
    
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
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            TTS(f"Recording audio for {recordTime[0]}")
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

def shutdownComputer():
    call('systemctl poweroff -i', shell=True)

def changeVolume():
    print("change volume")
    if hasNumbers(mainUser.userInput):
        print("has numbers")
        changeNumber = re.findall(r'\d+', mainUser.userInput)
        call(f'pactl -- set-sink-volume 0 {changeNumber[0]}% ', shell=True)
        return True
    else:
        print("has no numbers")
        return False

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
                    return True
                    if mainUser.hasAccess == True:
                        mainUser.hasAccess = False
                else:
                    commandFunc = self.commandFunction()
                    if commandFunc == True:
                        TTS(self.commandTrueSpeech)
                        return True
                    elif commandFunc == False:
                        TTS(self.commandFalseSpeech)
                        return True
                
            else:
                TTS("Are you sure you want to execute this command? If you are, run it again.")
                mainUser.hasAccess = True

class audioManager(Commands):
    audioDict = {}
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
                self.player = vlc.MediaPlayer(f"{mainUser.audioLocation}/{value}")
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


stopwatchManager = timeManager.stopwatch()

exitCommand = Commands("Exit", "Exit", exit, "Exitting.", "", False)
takeScreenshotCommand = Commands("Take a Screenshot", "Take", takeScreenshot, "Taking a screenshot", "", False)
showLatestScreenshotCommand = Commands("Show latest screenshot", "Show", showLatestScreenshot, "Showing the latest screenshot", "There is no latest screenshot", False)
timeCommand = Commands("Current time", "Time", getCurrentTime, f"The current time is {getCurrentTime().strftime("%I:%M %p")}", "", False)
audioCommands = audioManager("Playing audio")
recordingCommand = Commands("Record audio", "Record", recordAudio, "Recording has been finished.", "Please determine the length of the recording next time.", False)
shutdownCommand = Commands("Shutdown Computer", "shut down", shutdownComputer, "Shutting down computer.", "", True)
volumeCommand = Commands("Change Volume", "volume", changeVolume, "Volume has been changed.", "Please give a number to change the volume to next time.", False)
startStopwatchCommand = Commands("Start Stopwatch", "start", stopwatchManager.startStopwatch, "Starting stopwatch", "", False)

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
            print(mainUser.userInput)
            if commandExecution == True:
                mainUser.userInput = ""
                break





# # TTS(f"Good day, {username}")

# while False:


#




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
    

    

    

    



    


            
#     if "thank" in userInput.lower():
#         TTS(f"At your service, {username}.")
    
