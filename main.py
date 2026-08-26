# P.E.T.E.R v0 ALPHA

print("Starting PETER.")

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
import vlc
import random
import time
from accounts import accountSearch
import pyaudio
import sounddevice as sd
from scipy.io.wavfile import write
import pickle
import sys
import ttshandler
import timemodule

r = sr.Recognizer()

class User:
    def __init__(self, hasAccess=False, username="Guest", screenshotLocation="/home/mint/Pictures/", recordingLocation="/home/mint/Recordings", audioLocation="/home/mint/Music"):
        self.username = username
        self.hasAccess = hasAccess
        self.latestScreenshot = None
        self.screenshotLocation = screenshotLocation
        self.timezone = None
        self.userInput = ""
        self.recordingLocation = recordingLocation
        self.audioLocation = audioLocation
        self.isFirstTime = True
    
    def changeAccess(self, bool):
        self.hasAccess = bool

    def changeUsername(self, string):
        self.username = string

mainUser = User()

if os.path.getsize("Data/userData.pkl") > 0:
    with open("Data/userData.pkl", "rb") as userDataFile:
        mainUser = pickle.load(open("Data/userData.pkl", "rb"))

if mainUser.isFirstTime == True:
    ttshandler.TTS("As this is your first time, a configuration will be run.")
    print("As this is your first time, a configuration will be run.")
    ttshandler.TTS("Where do you want to save screenshots")
    mainUser.screenshotLocation = input("Where do you want to save screenshots? \n")
    ttshandler.TTS("Where do you want to save recordings?")
    mainUser.recordingLocation = input("Where do you want to save recordings? \n")
    ttshandler.TTS("Where do you want audio files to be run from?")
    mainUser.recordingLocation = input("Where do you want audio files to be run from? \n")
    ttshandler.TTS("What is your timezone?")
    mainUser.timezone = input("What is your timezone?")
    mainUser.isFirstTime = False
    with open("Data/userData.pkl", "ab") as userDataFile:
        pickle.dump(mainUser, userDataFile)
    ttshandler.TTS("Configuration has been finished. Launching the program.")
    print("Configuration has been finished. Launching the program.")
else:
    ttshandler.TTS("Good day")


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def recordAudio():
    recordTime = re.findall(r'\d+', mainUser.userInput)
    if hasNumbers(recordTime):
            fs = 44100  
            seconds = int(recordTime[0])
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            ttshandler.TTS(f"Recording audio for {recordTime[0]}")
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

def shutdownComputer():
    call('systemctl poweroff -i', shell=True)

def changeVolume():
    if hasNumbers(mainUser.userInput):
        changeNumber = re.findall(r'\d+', mainUser.userInput)
        call(f'pactl -- set-sink-volume 0 {changeNumber[0]}% ', shell=True)
        return True
    else:
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
                    print(self.commandTrueSpeech)
                    ttshandler.TTS(self.commandTrueSpeech)
                    self.commandFunction()
                    return True
                    if mainUser.hasAccess == True:
                        mainUser.hasAccess = False
                else:
                    commandFunc = self.commandFunction()
                    if commandFunc == True:
                        print(self.commandTrueSpeech)
                        ttshandler.TTS(self.commandTrueSpeech)
                        return True
                    elif commandFunc == False:
                        print(self.commandFalseSpeech)
                        ttshandler.TTS(self.commandFalseSpeech)
                        return True
                
            else:
                ttshandler.TTS("Are you sure you want to execute this command? If you are, run it again.")
                mainUser.hasAccess = True



class audioManager(Commands):
    audiolist = os.listdir(mainUser.audioLocation)
    commandsDict = None

    def __init__(self, commandSpeech):
        self.player = None
        self.latestAudioName = None
        self.audioLooping = None
        Commands.commandsList.append(self)
        self.commandsDict = {"play": self.playAudioCommand, "stop": self.stopAudio, "repeat": self.repeatAudio, "pause": self.pauseAudio, "resume": self.resumeAudio}
    
    def playAudioCommand(self, string):
        for audioFile in self.audiolist:
            audioFileName = audioFile.replace(".mp3", "")
            if audioFileName.lower() in string.lower():
                if self.player != None:
                    self.player.stop()
                    self.player = None
                self.latestAudioName = audioFileName
                self.player = vlc.MediaPlayer(f"{mainUser.audioLocation}/{audioFile}")
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
            splitString = string.split()
            for i in splitString:
                if key.lower() == i.lower():
                    commandExecution = value(string)
                    ttshandler.TTS(commandExecution)
                    return True

stopwatchManager = timemodule.stopwatch()


exitCommand = Commands("Exit", "Exit", sys.exit, "Exitting.", "", False)
takeScreenshotCommand = Commands("Take a Screenshot", "Take", takeScreenshot, "Taking a screenshot", "", False)
showLatestScreenshotCommand = Commands("Show latest screenshot", "Show", showLatestScreenshot, "Showing the latest screenshot", "There is no latest screenshot", False)
getStopwatchCommand = Commands("Get Time", "Stopwatch Time", stopwatchManager.getCurrentTime, "The", "", False)
timeCommand = Commands("Current time", "Time", getCurrentTime, f"The current time is {getCurrentTime().strftime("%I:%M %p")}", "", False)
recordingCommand = Commands("Record audio", "Record", recordAudio, "Recording has been finished.", "Please determine the length of the recording next time.", False)
shutdownCommand = Commands("Shutdown Computer", "shut down", shutdownComputer, "Shutting down computer.", "", True)
volumeCommand = Commands("Change Volume", "volume", changeVolume, "Volume has been changed.", "Please give a number to change the volume to next time.", False)
startStopwatchCommand = Commands("Start Stopwatch", "start", stopwatchManager.startStopwatch, "Starting stopwatch", "", False)
pauseStopwatchCommand = Commands("Pause Stopwatch", "pause stopwatch", stopwatchManager.pauseStopwatch, "Pausing the stopwatch", "The stopwatch is already paused.", False)
resumeStopwatchCommand = Commands("Resume Stopwatch", "resume stopwatch", stopwatchManager.resumeStopwatch, "Resuming the stopwatch", "The stopwatch is not paused.", False)
endStopwatchCOmmand = Commands("End Stopwatch", "end stopwatch", stopwatchManager.endStopwatch, "Ending the stopwatch", "A stopwatch is not running.", False)
audioCommands = audioManager("Playing audio")

while True:
    with sr.Microphone() as source:
        audio_text = r.listen(source)
    try:
        mainUser.userInput = r.recognize_google(audio_text, language="en-US")
    except sr.UnknownValueError:
        print("Whoops. Some problems on my end.")

    if audioCommands.player != None:
        if audioCommands.player.get_state() == vlc.State.Ended:
            if audioCommands.audioLooping == True:
                playAudioFunction = audioCommands.playAudioCommand(audioCommands.latestAudioName)
                print(playAudioFunction)
                print(audioCommands.latestAudioName)
                ttshandler.TTS(playAudioFunction)
            else:
                audioCommands.player = None
                audioCommands.latestAudioName = None

    if stopwatchManager.isRunning == True:
        stopwatchManager.manageStopwatch()
        stopwatchManager.getCurrentTime()

    if mainUser.userInput != "":
        for eachCommand in Commands.commandsList:
            commandExecution = eachCommand.executeCommand(mainUser.userInput)
            if commandExecution == True:
                mainUser.userInput = ""
                break