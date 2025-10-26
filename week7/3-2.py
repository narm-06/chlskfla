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

# 스위치 핀 설정
SW1 = 5  # 앞
SW2 = 6  # 오른쪽
SW3 = 13 # 왼쪽
SW4 = 19 # 뒤

# 모터 속도 설정 (듀티 사이클 50%)
MOTOR_SPEED = 50

# GPIO 초기 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# 모터 핀 출력 설정
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# 스위치 핀 입력 설정 (풀다운)
GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SW4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# PWM 객체 생성 (500Hz)
L_Motor = GPIO.PWM(PWMA, 500)
R_Motor = GPIO.PWM(PWMB, 500)

# PWM 시작 (정지 상태)
L_Motor.start(0)
R_Motor.start(0)

# 모터 정지
def stop_motors():
    L_Motor.ChangeDutyCycle(0)
    R_Motor.ChangeDutyCycle(0)

# 모터 제어
def control_motors(left_dir, right_dir, speed):
    # 왼쪽 모터 방향 설정
    GPIO.output(AIN1, left_dir[0])
    GPIO.output(AIN2, left_dir[1])
    L_Motor.ChangeDutyCycle(speed)

    # 오른쪽 모터 방향 설정
    GPIO.output(BIN1, right_dir[0])
    GPIO.output(BIN2, right_dir[1])
    R_Motor.ChangeDutyCycle(speed)

try:
    print("자동차 조종 시작. Ctrl+C로 종료")
    stop_motors()

    while True:
        # 스위치 입력 읽기
        sw1_val = GPIO.input(SW1)
        sw2_val = GPIO.input(SW2)
        sw3_val = GPIO.input(SW3)
        sw4_val = GPIO.input(SW4)

        if sw1_val == 1:
            # SW1: 앞 (정방향)
            print("SW1 click: 앞")
            control_motors((0, 1), (0, 1), MOTOR_SPEED)
        
        elif sw4_val == 1:
            # SW4: 뒤 (역방향)
            print("SW4 click: 뒤")
            control_motors((1, 0), (1, 0), MOTOR_SPEED)
            
        elif sw2_val == 1:
            # SW2: 오른쪽 (좌회전)
            print("SW2 click: 오른쪽")
            control_motors((0, 1), (0, 1), MOTOR_SPEED) 
            R_Motor.ChangeDutyCycle(MOTOR_SPEED * 0.2) # 오른쪽 속도 감소 (좌회전)
            
        elif sw3_val == 1:
            # SW3: 왼쪽 (우회전)
            print("SW3 click: 왼쪽")
            control_motors((0, 1), (0, 1), MOTOR_SPEED)
            L_Motor.ChangeDutyCycle(MOTOR_SPEED * 0.2) # 왼쪽 속도 감소 (우회전)
            
        else:
            # 스위치 미입력 시 정지
            stop_motors()
            
        time.sleep(0.01) # 딜레이

except KeyboardInterrupt:
    print("프로그램 종료.")
    pass

# 종료 시 정리
L_Motor.stop()
R_Motor.stop()
GPIO.cleanup()