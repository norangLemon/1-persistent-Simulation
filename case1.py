from random import *
from math import *

RUNNING_TIME = 10000 # 10 ** 8      # 100초
NODES = 5                   # node의 개수

node = []                   # 현재 line에 연결된 node 객체들
transmitting = []           # 현재 line에 data를 전송중인 node의 번호

collision = 0               # 총 packet 충돌 횟수
trial = 0                   # 총 packet 전송 시도 횟수
delay = 0                   # 총 delay 시간



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
T_ACK = 50          # time out 될 때까지 ack를 기다리는 시간

T_GEN = 10000       # pack 생성에 걸리는 평균 시간

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
    global T_ACK

    global T_GEN

    def __init__(self, number):

        self.state = 0              # 현재 state
        self.state_left = 0         # 현재 state를 더 유지해야 하는 시간

        self.number = number        # 이 노드의 번호

        self.busy = False           # idle sensing 중 다른 node가 전송하는 것을 감지함
        self.waiting_packet = False # packet이 생성되어 아직 전송완료를 대기중
        self.collision = False      # 현재 충돌이 난 상태인지 체크

        self.generate()

    def generate(self):
        # 전송할 새 packet을 생성한다
        self.state = ST_GEN_PACK
        x = random()
        while x == 0:
            x = random()
        self.state_left = round(-1 * T_GEN * log(x))
        print("gen [%d]: after %d" %(self.number, self.state_left))

    def backoff(self):
        self.state = ST_BACKOFF
        slot = T_CW * random()
        self.state_left = round(slot) * 50

    ## 외부에서 호출하는 함수들
    def process(self):
        # 이번 시간 프레임에 해야 할 일을 진행시킨다
        if self.state_left == 0:
            # 다음 state로 넘어간다
            if self.state == ST_GEN_PACK:
                # packet 생성 완료 -> idle인지 판단
                self.waiting_packet = True
                self.state = ST_SENSE_IDLE
                self.state_left = T_IDLE
 
            elif self.state == ST_SENSE_IDLE:
                # idle 50μs 유지됨 -> 전송
                self.state = ST_TRS_PACK
                self.state_left = T_PACK
                global trial
                trial += 1
                global transmitting
                transmitting.append(self.number)
            

            elif self.state == ST_TRS_PACK and self.collision == True:
                # 충돌 난 경우 -> 일단 연결 종료 후 50μs간 ack 기다리기
                global transmitting
                transmitting.remove(self.number)
                
                self.state = ST_WAIT_ACK
                self.state_left = T_ACK

            elif self.state == ST_TRS_PACK and self.collision == False:
                # 충돌 안 난 경우 -> 일단 연결 종료 후 1μs간 ack기다리기
                global transmitting
                transmitting.remove(self.number)

                self.state = ST_WAIT_ACK
                self.state_left = 1

            elif self.state == ST_WAIT_ACK and self.collision == True:
                # 충돌 난 경우 -> backoff하고 충돌 횟수 1 증가
                self.backoff()
                global collision
                collision += 1

            elif self.state == ST_WAIT_ACK and self.collision == False:
                # 충돌 안 난 경우 -> 다시 packet 생성
                self.waiting_packet = False
                self.generate()

            elif self.state == ST_BACKOFF:
                # backoff 끝남 -> 다시 idle인지 판단
                self.state = ST_SENSE_IDLE
                self.state_left = T_IDLE

        # busy한 경우 무조건 idle 할 때까지 기다린다.
        if self.state == ST_SENSE_IDLE and self.busy == True or self.state == ST_WAIT_IDLE and self.busy == True:
            # idle하지 않음 -> idle일때까지 계속 대기
            self.state = ST_WAIT_IDLE
            self.state_left = 1
        
        elif self.state == ST_WAIT_IDLE and self.busy == False:
            # line이 busy하지 않게 됨 -> 정말 idle인지 판단
            self.state = ST_SENSE_IDLE
            self.state_left = T_IDLE


        # 현재 state 1μs 진행
        print(self.state, end = " ")
        self.state_left -= 1

        if len(transmitting) != 0:
            self.busy = True
        else:
            self.busy = False
        
        if self.waiting_packet:
            global delay
            delay += 1

    def collide(self):
        # 충돌에 대한 처리를 한다
        self.collision = True


for num in range(0, NODES):
    node.append(Node(num))

for time in range(0, RUNNING_TIME):

    for n in range(0, NODES):
        # 이번 시간에 각 노드에서 수행하는 일을 진행시킴
        node[n].process()


    if len(transmitting) > 1:
        # 한번에 여러 노드가 전송중인 경우 충돌이 난 것
        for i in transmitting:
            node[i].collide()
    print("[%d] collision: %d trial: %d delay: %d" % (time, collision, trial, delay))

