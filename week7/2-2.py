#!/usr/bin/env python3

import time

try:
    import RPi.GPIO as GPIO
    ON_RPI = True
except Exception:
    GPIO = None
    ON_RPI = False

# 부저 연결 PIN
BUZZER_PIN = 12

# 경적음 설정 
HORN_FREQ = 440       # 라 음 (A)
HORN_DURATION = 0.3    # 한 번 울리는 시간(초)
PAUSE_DURATION = 0.2   # 두 번 사이 간격(초)
DUTY_CYCLE = 50        # PWM duty cycle (%)

def play_horn(pin=BUZZER_PIN):

    if not ON_RPI:

        time.sleep(HORN_DURATION * 2 + PAUSE_DURATION)
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    pwm = GPIO.PWM(pin, HORN_FREQ)
    pwm.start(0)

    try:
        for _ in range(2):  # 빵~빵~ 두 번 반복
            pwm.ChangeDutyCycle(DUTY_CYCLE)
            pwm.ChangeFrequency(HORN_FREQ)
            time.sleep(HORN_DURATION)
            pwm.ChangeDutyCycle(0)
            time.sleep(PAUSE_DURATION)
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    play_horn()
