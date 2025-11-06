import RPi.GPIO as GPIO
import time
import serial       # 시리얼 통신
import threading    # 스레딩
import math         # 삼각함수 계산

# --- 모터 핀 설정 (L298N 기준) ---
PWMA = 18   # 왼쪽 모터 PWM
AIN1 = 22   # 왼쪽 모터 방향 1
AIN2 = 27   # 왼쪽 모터 방향 2
PWMB = 23   # 오른쪽 모터 PWM
BIN1 = 25   # 오른쪽 모터 방향 1
BIN2 = 24   # 오른쪽 모터 방향 2

# 모터 최대 속도 설정 (0~100)
MOTOR_SPEED_MAX = 70 # 이 값을 조절해 최대 속도를 변경할 수 있습니다.

# --- 전역 변수: 조이스틱 데이터 저장 ---
gAngle = 0.0        # 각도 (0~360)
gMagnitude = 0.0    # 세기 (0.0~1.0)
gLastDataTime = time.time() # 마지막 수신 시간 (안전 정지용)

# --- GPIO 및 PWM 초기 설정 ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)

# PWM 객체 생성 (500Hz)
L_Motor = GPIO.PWM(PWMA, 500)
R_Motor = GPIO.PWM(PWMB, 500)
L_Motor.start(0) # 0% 듀티 사이클로 시작
R_Motor.start(0)

# --- 시리얼 포트 설정 ---
try:
    # 라즈베리파이 모델에 따라 '/dev/ttyS0' 또는 '/dev/serial0'
    ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
    print("Serial port opened successfully.")
except Exception as e:
    print(f"Error opening serial port: {e}")
    print("Check port, permissions, and raspi-config settings.")
    GPIO.cleanup()
    exit()

# === [V3] 새로운 모터 제어 함수 ===
# -100 ~ +100 범위의 속도를 입력받아 모터 방향과 PWM을 제어합니다.
def set_motors(left_speed, right_speed):
    # 속도 값이 -100 ~ 100 범위를 넘지 않도록 제한
    left_speed = max(min(left_speed, 100), -100)
    right_speed = max(min(right_speed, 100), -100)

    # --- 왼쪽 모터 제어 ---
    if left_speed > 0:
        # 전진
        GPIO.output(AIN1, 0)
        GPIO.output(AIN2, 1)
        L_Motor.ChangeDutyCycle(left_speed)
    elif left_speed < 0:
        # 후진
        GPIO.output(AIN1, 1)
        GPIO.output(AIN2, 0)
        L_Motor.ChangeDutyCycle(abs(left_speed))
    else:
        # 정지
        L_Motor.ChangeDutyCycle(0)

    # --- 오른쪽 모터 제어 ---
    if right_speed > 0:
        # 전진
        GPIO.output(BIN1, 0)
        GPIO.output(BIN2, 1)
        R_Motor.ChangeDutyCycle(right_speed)
    elif right_speed < 0:
        # 후진
        GPIO.output(BIN1, 1)
        GPIO.output(BIN2, 0)
        R_Motor.ChangeDutyCycle(abs(right_speed))
    else:
        # 정지
        R_Motor.ChangeDutyCycle(0)

# === 정지 함수 ===
def stop_motors():
    print("Command: STOP")
    set_motors(0, 0)

# === serial_thread 함수: 조이스틱 데이터를 파싱 ===
def serial_thread():
    global gAngle, gMagnitude, gLastDataTime
    while True:
        try:
            # 시리얼 포트에서 한 줄을 읽어옵니다.
            data = ser.readline()
            if data:
                # b'J0:183,0.7\r\n' -> 'J0:183,0.7'
                decoded_data = data.decode('utf-8').strip()
                
                # 'J0:'로 시작하는지 확인
                if decoded_data and decoded_data.startswith("J0:"):
                    # 'J0:183,0.7' -> '183,0.7'
                    parts = decoded_data.split(':')[1]
                    # '183,0.7' -> ['183', '0.7']
                    angle_mag = parts.split(',')
                    
                    if len(angle_mag) == 2:
                        try:
                            # 전역 변수에 각도와 세기 저장
                            gAngle = float(angle_mag[0])
                            gMagnitude = float(angle_mag[1])
                            gLastDataTime = time.time() # 마지막 수신 시간 갱신
                        except ValueError:
                            # 파싱 실패 시 (예: "J0:183,")
                            gMagnitude = 0.0 # 정지
        
        except Exception as e:
            print(f"Serial read error: {e}")
            gMagnitude = 0.0 # 에러 발생 시 정지
            time.sleep(1) # 에러 발생 시 1초 대기

# === [V4] 메인 프로그램 실행 (후진 스티어링 수정) ===
try:
    print("자동차 조종 시작 (V4 - 아날로그 믹싱 + 후진 스티어링 반전).")
    stop_motors() # 프로그램 시작 시 정지

    # 시리얼 스레드 시작
    t = threading.Thread(target=serial_thread)
    t.daemon = True  # 메인 프로그램 종료 시 스레드도 함께 종료
    t.start()
    print("Serial thread started.")

    WATCHDOG_TIMEOUT = 0.5 # 0.5초 동안 새 데이터가 없으면 정지
    DEADZONE = 0.2         # 조이스틱 중앙 데드존 (0.0 ~ 1.0)

    while True:
        # 1. Watchdog 타이머 확인
        if (time.time() - gLastDataTime) > WATCHDOG_TIMEOUT:
            if gMagnitude != 0.0: # 멈춰있지 않았을 때만 메시지 출력
                print("Watchdog timeout! Stopping car.")
            gMagnitude = 0.0 # 강제 정지

        # 2. 데드존 확인
        if gMagnitude < DEADZONE:
            set_motors(0, 0) # 정지
            time.sleep(0.01)
            continue # 루프 처음으로 돌아감

        # 3. 조이스틱 값 (폴라) -> X, Y (카테시안) 변환
        # 각도를 라디안으로 변환 (math.cos/sin은 라디안 사용)
        rad = gAngle * math.pi / 180.0
        
        # Y가 전진/후진 (sin), X가 좌/우 (cos)
        x_val = gMagnitude * math.cos(rad) 
        y_val = gMagnitude * math.sin(rad) 
        
        # 4. 아케이드 드라이브 믹싱 (X, Y -> Left, Right)
        
        # === [V4] 수정된 부분 ===
        # 만약 y_val (전진/후진)이 음수(후진)라면, 
        # x_val (좌/우) 스티어링을 반대로 뒤집습니다. (자동차 스타일)
        if y_val < 0:
            x_val = -x_val
        # ==========================

        # Y (전진/후진) + X (회전)
        # Y (전진/후진) - X (회전)
        left_raw = y_val + x_val
        right_raw = y_val - x_val

        # 5. 값 클램핑 (-1.0 ~ 1.0)
        # 대각선에서 1.0을 넘을 수 있으므로 정규화(클램핑)
        left_clamped = max(min(left_raw, 1.0), -1.0)
        right_clamped = max(min(right_raw, 1.0), -1.0)

        # 6. PWM 값으로 스케일링 (-MOTOR_SPEED_MAX ~ +MOTOR_SPEED_MAX)
        left_speed_pwm = left_clamped * MOTOR_SPEED_MAX
        right_speed_pwm = right_clamped * MOTOR_SPEED_MAX

        # 7. 모터에 최종 속도 적용
        set_motors(left_speed_pwm, right_speed_pwm)
        
        # 디버깅용 출력 (필요하면 주석 해제)
        # print(f"A:{gAngle:.0f} M:{gMagnitude:.1f} | X:{x_val:.2f} Y:{y_val:.2f} | L:{left_speed_pwm:.1f} R:{right_speed_pwm:.1f}")

        time.sleep(0.01) # 메인 루프 딜레이 (CPU 과부하 방지)

except KeyboardInterrupt:
    print("프로그램 종료 (Ctrl+C).")
    pass

finally:
    # 프로그램 종료 시 정리
    print("Cleaning up GPIO and closing serial port.")
    stop_motors() # 모터 정지
    GPIO.cleanup()
    ser.close()
    print("Cleanup complete. Exiting.")