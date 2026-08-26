import pyttsx3
engine = pyttsx3.init()

def TTS(Text):
    engine.say(Text)
    engine.setProperty('rate', 125) 
    engine.runAndWait() 