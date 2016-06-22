RUNNING_TIME = 1000000000   # 1000초
NODES = 2                   # node의 개수

node = []                   # 현재 line에 연결된 node 객체들
transmitting = []           # 현재 line에 data를 전송중인 node의 번호

collision = 0               # 총 packet 충돌 횟수
success = 0                 # 총 packet 전송 성공 횟수
delay = 0                   # 총 delay 시간

for num in range(1, NODES):
    node.append(Node(1))

for time in range(1, RUNNING_TIME):

    for n in range(1, NODES):
        # 이번 시간에 각 노드에서 수행하는 일을 진행시킴
        node[n].process()

    if len(transmitting) > 1:
        # 한번에 여러 노드가 전송중인 경우 충돌이 난 것
        for n in transmitting:
            node[n].collide()
            collision += 1


# Throughput = (sum of success)/(total time)
# Mean packet delay = (Sum of delays)/(Total success)
# Transmission collision probability = (Num. of collision)/(Total trial)



