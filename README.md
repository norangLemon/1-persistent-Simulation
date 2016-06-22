Data Communication: Simulation HW
-----

2016년 1학기 데이타통신 기말과제

## Introduction

## System description

## Simulation model

### 기본 가정
* 모든 event는 1μs 단위로 일어난다고 가정한다.
따라서 μs 단위로 소숫점 아래의 숫자는 모두 반올림한다.
* 모든 packet은 node들로 전달되는 것이 아니라, 외부로 전달되는 것으로 가정한다.
* 외부 노드에서는 ack(1-persistent CSMA w/o CD인 경우) 이외의 다른 packet은 들어오지 않는다.

### 1-persistent CSMA
* 전송이 성공한 경우, ack는 즉각적으로 전송된다.
* ack의 전송 시간은 1μs로 가정한다.
* time-out은 전송 완료로부터 50μs로 설정한다.
이 시간이 지나도록 ack를 받지 못하면 전송에 실패한 것으로 판단한다.
* 간결한 구현을 위해서, 충돌시에 node 객체에게 충돌 사실을 바로 알린다.
이때 node 객체는 전송을 중단시키지 않고 계속한다.
전송이 완료된 후에는 충돌 여부에 따라 하는 행동이 달라진다.
    * 충돌된 경우: 전송 종료 후 50μs 후에 재전송 시도
    * 충돌하지 않은 경우: 전송 종료 후 1μs동안 ack를 받고 새 패킷 생성을 시작한다. 
이때 ack를 보내는 node의 번호를 편의상 ack를 받는 node의 번호로 설정한다.
ack 전송 시작과 끝을 해당 node에서 관리한다.

## Numerical results & Discussion
## Conclusion


