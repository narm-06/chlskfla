#!/usr/bin/env python3

import time

# Raspberry Pi 전용 라이브러리. 
try:
    import RPi.GPIO as GPIO
    ON_RPI = True
except Exception:
    GPIO = None
    ON_RPI = False

# --- 음계 주파수 (Hz) ---
NOTES = {
    "도": 262,  # C
    "레": 294,  # D
    "미": 330,  # E
    "파": 349,  # F
    "솔": 392,  # G
    "라": 440,  # A
    "시": 494,  # B
    "도_high": 523,  # 높은 옥타브의 도
}

# 출력할 음계 순서
SCALE = ["도", "레", "미", "파", "솔", "라", "시", "도_high"]

# 부저 연결 PIN 
BUZZER_PIN = 12

# 연주 파라미터
NOTE_DURATION = 0.5  # 각 음 길이(초)
DUTY_CYCLE = 50      # PWM duty cycle (%)

def play_scale(pin=BUZZER_PIN, duration=NOTE_DURATION):
    if not ON_RPI:
        # 시뮬레이션 모드에서는 아무 동작도 하지 않음
        for _ in SCALE:
            time.sleep(duration)
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    pwm = GPIO.PWM(pin, 440)
    pwm.start(DUTY_CYCLE)
    try:
        for name in SCALE:
            freq = NOTES.get(name)
            if freq is None:
                continue
            pwm.ChangeFrequency(freq)
            time.sleep(duration)
            pwm.ChangeDutyCycle(0)
            time.sleep(0.05)
            pwm.ChangeDutyCycle(DUTY_CYCLE)
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    play_scale()