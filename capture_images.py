#save images for cabulation

import cv2 as cv
import os
import socket
import threading
import time
import numpy as np
#↓↓↓Start taking images code↓↓↓
Chess_Board_Dimensions = (9, 6)

n = 0  # image counter

# checks images dir is exist or not
image_path = "images"

Dir_Check = os.path.isdir(image_path)

if not Dir_Check:  # if directory does not exist, a new one is created
    os.makedirs(image_path)
    print(f'"{image_path}" Directory is created')
else:
    print(f'"{image_path}" Directory already exists.')

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def detect_checker_board(image, grayImage, criteria, boardDimension):
    ret, corners = cv.findChessboardCorners(grayImage, boardDimension)
    if ret == True:
        corners1 = cv.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)
        image = cv.drawChessboardCorners(image, boardDimension, corners1, ret)

    return image, ret
#↑↑↑End of taking images code ↑↑↑

#↓↓↓Start of capturing of tello camera ↓↓↓
# データ受け取り用の関数(thread処理をするので割り込みで行われる)
def udp_receiver():
    while True:
        try:
            response, _ = sock.recvfrom(1024)
        except Exception as e:
            print(e)
            break


# Tello側のローカルIPアドレス(デフォルト)、宛先ポート番号(コマンドモード用)
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889
TELLO_ADDRESS = (TELLO_IP, TELLO_PORT)

# Telloからの映像受信用のローカルIPアドレス、宛先ポート番号
TELLO_CAMERA_ADDRESS = 'udp://@0.0.0.0:11111'

# キャプチャ用のオブジェクト
cap = None

# データ受信用のオブジェクト備
response = None

# 通信用のソケットを作成
# ※アドレスファミリ：AF_INET（IPv4）、ソケットタイプ：SOCK_DGRAM（UDP）
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 自ホストで使用するIPアドレスとポート番号を設定
sock.bind(('', TELLO_PORT))

# 受信用スレッドの作成
thread = threading.Thread(target=udp_receiver, args=())
thread.daemon = True
thread.start()

threading.Thread(target=detect_checker_board, daemon=True).start()


# コマンドモード
sock.sendto('command'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(1)

# カメラ映像のストリーミング開始
sock.sendto('streamon'.encode('utf-8'), TELLO_ADDRESS)

time.sleep(5)

if cap is None:
    cap = cv.VideoCapture(TELLO_CAMERA_ADDRESS)

if not cap.isOpened():
    cap.open(TELLO_CAMERA_ADDRESS)

time.sleep(1)


while True:
    _, frame = cap.read()
    copyFrame = frame.copy()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    image, board_detected = detect_checker_board(
        frame, gray, criteria, Chess_Board_Dimensions
    )
    if frame is None or frame.size == 0:
        continue


    # print(ret)
    cv.putText(
        frame,
        f"saved_img : {n}",
        (30, 40),
        cv.FONT_HERSHEY_PLAIN,
        1.4,
        (0, 255, 0),
        2,
        cv.LINE_AA,
    )

    #cv.imshow("frame", frame)
    # copyframe; without augmentation
    cv.imshow("copyFrame", copyFrame)

    key = cv.waitKey(1)

    if key == ord("q"):
        break
    if key == ord("s") and board_detected == True:
        # the checker board image gets stored
        cv.imwrite(f"{image_path}/image{n}.png", copyFrame)

        print(f"saved image number {n}")
        n += 1  # the image counter: incrementing
cap.release()
cv.destroyAllWindows()

print("Total saved Images:", n)
