import RPi.GPIO as GPIO
import time

# 모터 A (왼쪽) 핀 설정
PWMA = 18
AIN1 = 22
AIN2 = 27

# 모터 B (오른쪽) 핀 설정
PWMB = 23
BIN1 = 25
BIN2 = 24

# GPIO 설정
GPIO.setwarnings(False) # 경고 메시지 무시
GPIO.setmode(GPIO.BCM)  # BCM 모드 사용

# 모터 A 핀 설정
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)

# 모터 B 핀 설정
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# PWM 객체 생성 (주파수 500Hz)
L_Motor = GPIO.PWM(PWMA, 500)
R_Motor = GPIO.PWM(PWMB, 500)

# PWM 시작 (초기 듀티 사이클 0%, 정지)
L_Motor.start(0)
R_Motor.start(0)

try:
    while True:
        # 1. 모터 정방향 50% 듀티 사이클로 동작 (1.0초)

        # 왼쪽 모터 정방향
        GPIO.output(AIN1, 0)
        GPIO.output(AIN2, 1)
        L_Motor.ChangeDutyCycle(50)

        # 오른쪽 모터 정방향
        GPIO.output(BIN1, 0)
        GPIO.output(BIN2, 1)
        R_Motor.ChangeDutyCycle(50)

        time.sleep(1.0) # 1초 동작

        # 2. 모터 정지 (1.0초)

        # 왼쪽 모터 정지
        L_Motor.ChangeDutyCycle(0)

        # 오른쪽 모터 정지
        R_Motor.ChangeDutyCycle(0)

        time.sleep(1.0) # 1초 정지

except KeyboardInterrupt:
    pass # Ctrl+C 입력 시 루프 종료

# 초기화
L_Motor.stop()
R_Motor.stop()
GPIO.cleanup()