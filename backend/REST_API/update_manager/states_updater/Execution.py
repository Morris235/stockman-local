from StatesMining import StatesMining
from StatesUpdater import StatesUpdater
from StatesModifyUpdater import StatesModifyUpdater
import socket
import time
from datetime import datetime

completed = False
count = 0

while completed is False:

    ipaddress = socket.gethostbyname(socket.gethostname())

    # 인터넷 연결 확인
    if ipaddress == "127.0.0.1":
        count += 1
        sec = 60
        tmnow = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{tmnow}] 인터넷 연결이 없습니다. {sec} 초 동안 대기합니다 ({count}).')

        time.sleep(sec)
    else:
        StatesMining()  # 연말에 기업들이 사업보고서를 제출하면 실행
        StatesUpdater()  # StatesMining()이 완료되면 실행
        StatesModifyUpdater()  # StatesUpdater()가 완료되면 실행 (상장폐지 종목제거 모듈 import)
        print('업데이트 완료')
        completed = True
