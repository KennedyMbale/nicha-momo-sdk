import time

def countdown(seconds):
    while seconds >= 1:
        time.sleep(1)
        seconds -= 1
    return