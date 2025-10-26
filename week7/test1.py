#!/usr/bin/env python3
import time

try:
    import RPi.GPIO as GPIO
    ON_RPI = True
except Exception:
    GPIO = None
    ON_RPI = False

# --- BCM 모드 기준 ---
BUZZER_BCM = 12
SWITCH_PINS = [5, 6, 13, 19]  # SW1~SW4

# --- 음계 주파수 (Hz) ---
TONE = {
    "C": 262,   # 도
    "D": 294,   # 레
    "E": 330,   # 미
    "F": 349    # 파
}

# --- 스위치와 음계 매핑 ---
NOTE_MAP = {
    5: "C",   # SW1 → 도
    6: "D",   # SW2 → 레
    13: "E",  # SW3 → 미
    19: "F"   # SW4 → 파
}

# --- PWM 설정 ---
DUTY_CYCLE = 50
NOTE_DURATION = 0.4  # 한 음 재생 시간(초)

def play_tone(pin, freq, duration):
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, freq)
    pwm.start(DUTY_CYCLE)
    time.sleep(duration)
    pwm.stop()

def main():
    if not ON_RPI:
        return  # 시뮬레이션 출력 제거

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_BCM, GPIO.OUT)
    for pin in SWITCH_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    prev_state = {pin: GPIO.LOW for pin in SWITCH_PINS}

    try:
        while True:
            for pin in SWITCH_PINS:
                curr = GPIO.input(pin)
                # 눌리는 순간만 감지 (LOW → HIGH)
                if prev_state[pin] == GPIO.LOW and curr == GPIO.HIGH:
                    note = NOTE_MAP[pin]
                    freq = TONE[note]
                    play_tone(BUZZER_BCM, freq, NOTE_DURATION)
                prev_state[pin] = curr
            time.sleep(0.02)  # 디바운스
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
