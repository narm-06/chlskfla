#!/usr/bin/env python3
import time

try:
    import RPi.GPIO as GPIO
    ON_RPI = True
except Exception:
    GPIO = None
    ON_RPI = False


BUZZER_BCM = 12   # 부저: GPIO12
SWITCH_BCM = 5    # 스위치: GPIO5


HORN_FREQ = 440
HORN_DURATION = 0.3
PAUSE_DURATION = 0.2
DUTY_CYCLE = 50

def play_horn(pin=BUZZER_BCM):
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, HORN_FREQ)
    pwm.start(0)
    try:
        for _ in range(2):  
            pwm.ChangeFrequency(HORN_FREQ)
            pwm.ChangeDutyCycle(DUTY_CYCLE)
            time.sleep(HORN_DURATION)
            pwm.ChangeDutyCycle(0)
            time.sleep(PAUSE_DURATION)
    finally:
        pwm.stop()

def main():
    if not ON_RPI:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_BCM, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUZZER_BCM, GPIO.OUT)

    prev_state = GPIO.LOW

    try:
        while True:
            curr_state = GPIO.input(SWITCH_BCM)
            if prev_state == GPIO.LOW and curr_state == GPIO.HIGH:
                play_horn(BUZZER_BCM)
            prev_state = curr_state
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()