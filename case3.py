from random import *
from math import *

RUNNING_TIME = 10 ** 6      # 1초

NODES = 0                   # node의 개수
CW = 32                     # uniform CW

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
ST_BACKOFF = 4      # back off 만큼 기다리는 중

T_IDLE = 50         # idle sense하는 시간
T_PACK = 819        # packet 전송 시간

T_GEN = 10000       # pack 생성에 걸리는 평균 시간

class Node: 

    def __init__(self, number):

        self.state = 0              # 현재 state
        self.state_left = 0         # 현재 state를 더 유지해야 하는 시간

        self.number = number        # 이 노드의 번호

        self.busy = False           # idle sensing 중 다른 node가 전송하는 것을 감지함
        self.waiting_packet = False # packet이 생성되어 아직 전송완료를 대기중
        self.collision = False      # 현재 충돌이 난 상태인지 체크
        self.collided = False       # 직전에 충돌이 난 상태인지 체크
        self.CW = 2                 # 충돌 횟수에 따라서 node의 CW가 커지게 됨

        self.generate()

    def generate(self):
        global ST_GEN_PACK
        # 전송할 새 packet을 생성한다
        self.state = ST_GEN_PACK
        x = random()
        while x == 0:
            x = random()
        self.state_left = round(-1 * T_GEN * log(x))

    def backoff(self):
        global CW
        self.state = ST_BACKOFF
        if self.collided and self.CW <= CW:
            self.CW = 2* self.CW               # 직전에 충돌이 일어난 경우 CW를 2배
        else:
            self.CW = 2                  # 일어나지 않은 경우 초기화
        slot = randrange(1, CW+1)
        self.state_left = slot * 50
        self.collided = True        # 현재 충돌이 났음을 저장
        self.collision = False      # 현재의 충돌이 해소되었으므로 상태 제거

    ## 외부에서 호출하는 함수들
    def process(self):
        global ST_GEN_PACK
        global ST_SENSE_IDLE
        global ST_WAIT_IDLE
        global ST_TRS_PACK
        global ST_BACKOFF 

        global T_IDLE
        global T_PACK

        global T_GEN
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
                # 충돌 난 경우 -> 일단 연결 종료 후 back off
                global transmitting
                transmitting.remove(self.number)
                
                self.backoff()
                global collision
                collision += 1

            elif self.state == ST_TRS_PACK and self.collision == False:
                # 충돌 안 난 경우 -> 연결 종료 후 새 패킷 생성 대기
                global transmitting
                transmitting.remove(self.number)

                self.waiting_packet = False
                self.collided = False
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
        #print("[%d] %d" %(self.state, self.state_left), end = " ")
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
        self.state_left = 0     # 충돌 즉시 전송이 종료됨


def Throughput(trial, collision):
    global RUNNING_TIME
    return (trial - collision)* 1000000/RUNNING_TIME

def MeanDelay(delay, trial, collision):
    return delay/(trial - collision)

def CollisionPlob(trial, collision):
    return collision/trial

if __name__ == "__main__":

    node_list = [5, 10, 15, 20, 25]
    CW_list = [32, 64, 128]

    print("Nodes CW Throughput M_delay Col_prob.") 
    for NODES_ in node_list:
        NODES = NODES_
        for CW_ in CW_list:
            CW = CW_
            
            cnt = 5
            while cnt > 0:
                cnt -= 1
                
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
                    #print("{%d} collision: %d trial: %d delay: %d" % (time, collision, trial, delay))
                
                t = Throughput(trial, collision)
                m = MeanDelay(delay, trial, collision)
                c = CollisionPlob(trial, collision)
                print("%d %d %0.2f %0.2f %0.2f" % (NODES, CW, t, m, c)) 
                trial = 0
                collision = 0
                delay = 0
                transmitting = []
                node = []
