from random import *
from math import *

## state의 종류
ST_GEN_PACK = 0     # packet 생성중
ST_SENSE_IDLE = 1   # idle인지 sensing 중
ST_WAIT_IDLE = 2    # idle이 될 때까지 기다리는 중
ST_TRS_PACK = 3     # packet 전송중
ST_WAIT_ACK = 4     # ack 기다리는 중
ST_BACKOFF = 5      # back off 만큼 기다리는 중

T_IDLE = 50         # idle sense하는 시간
T_PACK = 819        # packet 전송 시간
T_CW = 32*50        # uniform CW

class Node: 
    global ST_GEN_PACK
    global ST_SENSE_IDLE
    global ST_WAIT_IDLE
    global ST_TRS_PACK
    global ST_WAIT_ACK
    global ST_BACKOFF 

    global T_IDLE
    global T_PACK
    global T_CW

    global delay
    global transmitting

    def __init__(self):

        self.delay = 0              # 현재 packet의 전송 dealy 시간
        self.state = 0              # 현재 state
        self.state_left = 0         # 현재 state를 더 유지해야 하는 시간

        self.busy = False           # idle sensing 중 다른 node가 전송하는 것을 감지함
        self.waiting_packet = False # packet이 생성되어 아직 전송완료를 대기중
        self.collision = False      # 현재 충돌이 난 상태인지 체크

    def generate(self):
        # 전송할 새 packet을 생성한다
        self.state = ST_GEN_PACK
        x = random
        while x == 0:
            x = random()
        self.state_left = round(-10000 * log(x))

        print("generate packet: "+ str(self.state_left))

    def backoff(self):
        self.state = ST_BACKOFF
        time = T_CW * rand() * 50
        self.state_left = round(time)

    ## 외부에서 호출하는 함수들
    def process(self):
        # 이번 시간 프레임에 해야 할 일을 진행시킨다
        if self.state_left == 0:
            # 다음 state로 넘어간다
            print(state)
            if self.state == ST_GEN_PACK:
                # packet 생성 완료 -> idle인지 판단
                self.waiting_packet = True
                self.state = ST_SENSE_IDLE
                self.state_left = T_IDLE

            elif self.state == ST_SENSE_IDLE and self.busy == True or self.state == ST_WAIT_IDLE and self.busy == True:
                # idle하지 않음 -> idle일때까지 계속 대기
                self.state = ST_WAIT_IDLE
                self.state_left = 1

            elif self.state == ST_SENSE_IDLE and self.busy == False:
                # idle함 -> 전송
                self.state = ST_TRS_PACK
                self.state_left = T_PACK
            
            elif self.state == ST_WAIT_IDLE and self.busy == False:
                # line이 busy하지 않게 됨 -> 정말 idle인지 판단
                self.state = ST_SENSE_IDLE
                self.state = T_IDLE

            elif self.state == ST_TRS_PACK and self.collision == True:
                # 충돌 난 경우 -> backoff함
                self.backoff()

            elif self.state == ST_TRS_PACK and self.collision == False:
                # 충돌 안 난 경우 -> 다시 packet 생성
                self.waiting_packet = False
                self.generate()

            elif self.state == ST_BACKOFF:
                # backoff 끝남 -> 다시 idle인지 판단
                self.state = ST_SENSE_IDLE
                self.state_left = T_IDLE
 
            # 현재 state 1μs 진행
            self.state_left -= 1
            if len(transmitting) != 0:
                self.busy = True
            if self.waiting_packet:
                self.delay += 1
            elif not self.waiting_packet and self.delay != 0:
                delay += self.delay

    def collide(self):
        # 충돌에 대한 처리를 한다
        print ("collide")
        self.collision = True
        self.state_left += 50    # ack를 기다리는 시간 추가
