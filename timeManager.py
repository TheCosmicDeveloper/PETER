import time

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
        self.isRunning = False
        self.endTime = self.currentTime
        self.currentTime = 0
    
    def pauseStopwatch(self):
        self.isRunning = False
        self.isPaused = True
    
    def resumeStopwatch(self):
        self.isRunning = True
        self.isPaused = False

stopwatchManager = stopwatch()

while True:
    if stopwatchManager.isRunning == True:
        stopwatchManager.currentTime = time.time() - stopwatchManager.startTime
        print(stopwatchManager.currentTime)





#     if "timer" in userInput.lower():
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