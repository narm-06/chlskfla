# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

# BCM 핀 번호 모드 설정
GPIO.setmode(GPIO.BCM)

# 4개의 스위치 핀 번호 설정 (SW1~SW4)
switch_pins = [5, 6, 13, 19]

# 각 스위치를 입력으로 설정 
for pin in switch_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 이전 상태 리스트 (초기값 0)
prev_states = [0, 0, 0, 0]

print("스위치 입력 대기 중입니다... (Ctrl+C로 종료)\n")

try:
    while True:
        for i, pin in enumerate(switch_pins):
            current_state = GPIO.input(pin)
            
            # 0 -> 1 변화(스위치 눌림) 시 동작
            if prev_states[i] == 0 and current_state == 1:
                print((f'SW{i+1} click', i+1))  # 스위치 번호와 같은 숫자 출력
            
            # 현재 상태 업데이트
            prev_states[i] = current_state
        
        time.sleep(0.05)  # 채터링 방지용 딜레이

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    GPIO.cleanup()