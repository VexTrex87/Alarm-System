from cuesdk import CueSdk
from gtts import gTTS 
import pygame
import os
import queue
import threading
import time
import shutil
import playsound

WAVE_DURATION = 400
PULSE_DELAY = 0.01
ALARM_VOLUME = 1
LANGUAGE = "en"

def play_sound(path, volume = 1, does_loop = 0):
    new_sound = pygame.mixer.Sound(path) 
    new_sound.set_volume(volume) 
    new_sound.play(does_loop) 

def output_message(message):
    print(message)
    audio = gTTS(text = message, lang = LANGUAGE, slow = False) 
    file_name = "TTS\\output_message.mp3"
    delete_contents("TTS")
    audio.save(file_name) 
    playsound.playsound(file_name)

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

def watch_input(inputQueue):
    while (True):
        input_str = input()
        inputQueue.put(input_str)

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

def main():
    output_message("Alarm system starting...")

    global sdk
    sdk = CueSdk()

    print("Activating sounds...")
    os.system("UseSpeakersForAlarm.bat")
    pygame.mixer.init()
    play_sound("Alarm.mp3", ALARM_VOLUME, -1)
    print("Sound activated")

    print("Activating input reader...")
    inputQueue = queue.Queue()
    threading.Thread(
        target = watch_input,
        args = (inputQueue,),
        daemon = True
    ).start()
    print("Input reader activated")

    print("Connecting to light system...")
    if not sdk.connect():
        errorMessage = sdk.get_last_error()
        output_message("Could not connect: %s" % errorMessage)
        return
    print("Light system connected")
    
    print("Retrieving light devices...")
    device_count = sdk.get_device_count()  
    devices = sdk.get_devices()  
    print(f"{str(device_count)} devices found: {devices}")

    print("Retrieving colors of light devices...")
    colors = get_available_leds()
    if not colors:
        output_message("Could not retrieve colors")
        return
    print("Colors of light devices retrieved")

    output_message("Alarm system started")
    print("Alarm system started, type \"exit\" to stop program")
    while (True):
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()
            if input_str.lower() == "exit":
                output_message("Stopping program...")
                pygame.mixer.stop()
                delete_contents("TTS")
                print("Program stopped")
                return

        perform_pulse_effect(WAVE_DURATION, colors)
        time.sleep(PULSE_DELAY)

main()