WAVE_DURATION = 400
PULSE_DELAY = 0.01
ALARM_VOLUME = 1
LANGUAGE = "en"

from cuesdk import CueSdk
from gtts import gTTS 
import speech_recognition
import pygame
import os
import queue
import threading
import time
import shutil
import playsound

sdk = CueSdk()

def delete_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
    return leds

def perform_pulse_effect(wave_duration, all_leds):
    time_per_frame = 25
    x = 0
    cnt = len(all_leds)
    dx = time_per_frame / wave_duration
    while x < 2:
        val = int((1 - (x - 1) ** 2) * 255)
        for di in range(cnt):
            device_leds = all_leds[di]
            for led in device_leds:
                device_leds[led] = (val, 0, 0)  # red
            sdk.set_led_colors_buffer_by_device_index(di, device_leds)
        sdk.set_led_colors_flush_buffer()
        time.sleep(time_per_frame / 1000)
        x += dx

def play_sound(path, volume = 1, does_loop = 0):
    new_sound = pygame.mixer.Sound(path) 
    new_sound.set_volume(volume) 
    new_sound.play(does_loop) 

def say_text(message):
    print(message)
    audio = gTTS(text = message, lang = LANGUAGE, slow = False) 
    file_name = "TTS\\output_message.mp3"
    delete_contents("TTS")
    audio.save(file_name) 
    playsound.playsound(file_name)


def get_voice():
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except Exception as error_message:
            if error_message:
                print(f"VOICE ERROR: {error_message}")

def watch_text(text_queue):
    while (True):
        text_queue.put(input().lower())

def watch_voice(voice_queue):
    while (True):
        voice_text = get_voice()
        if voice_text:
            voice_queue.put(voice_text.lower())

def create_queue(callback):
    new_queue = queue.Queue()
    threading.Thread(
        target = callback,
        args = (new_queue,),
        daemon = True
    ).start()

    return new_queue


def stop_alarm():
    say_text("Stopping alarm...")
    pygame.mixer.stop()
    say_text("Alarm stopped and must be restarted to run properly. Awaiting voice command...")

def start_alarm():
    say_text("Starting alarm...")
    play_sound("Alarm.mp3", ALARM_VOLUME, -1)

    if not sdk.connect():
        errorMessage = sdk.get_last_error()
        say_text("Could not connect to SDK: %s" % errorMessage)
        return

    device_count = sdk.get_device_count()  
    devices = sdk.get_devices()  
    print(f"{str(device_count)} devices found: {devices}")

    colors = get_available_leds()
    if not colors:
        say_text("Could not retrieve colors")
        return

    say_text("Alarm started, awaiting voice command...")
    text_queue.queue.clear()
    voice_queue.queue.clear()
    while (True):
        latest_text = (text_queue.qsize() > 0) and text_queue.get().lower()
        latest_voice = (voice_queue.qsize() > 0) and voice_queue.get().lower()

        if (latest_text == "stop") or (latest_voice and "stop" in latest_voice):
            stop_alarm()
            break

        perform_pulse_effect(WAVE_DURATION, colors)
        time.sleep(PULSE_DELAY)

def main():
    global text_queue
    text_queue = create_queue(watch_text)

    global voice_queue
    voice_queue = create_queue(watch_voice)

    pygame.mixer.init()
    os.system("usespeakers")
    say_text("Program started, awaiting voice command...")

    text_queue.queue.clear()
    voice_queue.queue.clear()
    while (True):
        latest_text = (text_queue.qsize() > 0) and text_queue.get().lower()
        latest_voice = (voice_queue.qsize() > 0) and voice_queue.get().lower()

        if (latest_text == "start") or (latest_voice and "start" in latest_voice):
            start_alarm()
        elif (latest_text == "exit") or (latest_voice and "exit" in latest_voice):
            say_text("Exiting program...")
            break

main()