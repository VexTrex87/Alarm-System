from gtts import gTTS
import speech_recognition as sr
import os
import time
import playsound

def speak(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception as e:
            print("Exception: " + str(e))

        return said

speak("Microphone ready...")
text = get_audio().lower()
print(text)
if "jack" in text:
    if "start" in text:
        speak("Starting alarm system")
    elif "stop" in text:
        speak("Stopping alarm system")