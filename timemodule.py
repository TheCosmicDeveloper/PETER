import ttshandler
import time
import datetime

def secondsToTime(seconds):
    seconds = (datetime.timedelta(seconds=seconds))
    seconds = str(seconds)
    seconds = seconds.replace(":", " ")
    seconds = seconds.split()

    hours = seconds[0]
    minutes = seconds[1]
    seconds = seconds[2]
    miliseconds = ""
    seconds = list(seconds)
    for i in reversed(seconds):
        if i != ".":
            seconds.remove(i)
            miliseconds += i
            print(seconds)
        else:
            seconds.remove(i)
            seconds = "".join(seconds)
            miliseconds = reversed(miliseconds)
            miliseconds = "".join(miliseconds)
            miliseconds = str(miliseconds.replace("0", ""))
            print
            break

    miliseconds = list(miliseconds)
    for i in reversed(miliseconds):
        if len(miliseconds) > 3:
            miliseconds.remove(i)
        else:
            miliseconds = "".join(miliseconds)
            break
    return hours, minutes, seconds, miliseconds


class stopwatch():
    def __init__(self):
        self.startTime = 0
        self.currentTime = 0
        self.endTime = 0
        self.isRunning = False
        self.isPaused = False
    
    def startStopwatch(self):
        self.startTime = time.time()
        self.isRunning = True
    
    def endStopwatch(self):
        if self.isRunning == True:
            self.isRunning = False
            self.endTime = self.currentTime
            self.currentTime = 0
            return True
        else:
            return False
    
    def pauseStopwatch(self):
        if self.isPaused == False:    
            self.isRunning = False
            self.isPaused = True
            return True
        else:
            return False
    
    def resumeStopwatch(self):
        if self.isPaused == True:
            self.isRunning = True
            self.isPaused = False
            return True
        else:
            return False
    
    def getCurrentTime(self):
        hours, minutes, seconds, miliseconds = secondsToTime(self.currentTime)
        print(f"The current stopwatch time is {hours} hours, {minutes} minutes, {seconds} seconds and {miliseconds} miliseconds")
        # ttshandler.TTS(f"The current stopwatch time is {hours} hours, {minutes} minutes, {seconds} seconds and {miliseconds} miliseconds")

    def manageStopwatch(self):
        self.currentTime = time.time() - self.startTime
        