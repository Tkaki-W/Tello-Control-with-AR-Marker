import cv2 as cv
from cv2 import aruco
import os
import socket
import threading
import time
import numpy as np


#キャリブレーションマトリックスの読み取り
calib_data_path = "calib_data/MultiMatrix.npz"

calib_data = np.load(calib_data_path)
print(calib_data.files)
#armakerの位置読み取りの時にcam_mat dist_coefを使用
cam_mat = calib_data["camMatrix"]
dist_coef = calib_data["distCoef"]
r_vectors = calib_data["rVector"]
t_vectors = calib_data["tVector"]

MARKER_SIZE = 4  # centimeters (measure your printed marker size)

marker_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_250)

param_markers = aruco.DetectorParameters()

#以下threadでデータを取り扱うにあたりのデータ設定
latest_data = {"id":None, "distance":None, "x":None, "y":None, "roll":None, "pitch":None, "yaw":None}
data_lock=threading.Lock()

#以下はbを押されたかを保存する変数
push_b = False
#制御の距離・角度・座標のの変数
min_distance = 60
max_distance = 110
min_degree = -20
max_degree = 20
 #座標に関してはカメラの原点とカメラの中心が一致していないのでminを大きめにとる
min_xposition = -25
max_xposition = 15

#↓↓↓Start of capturing of tello camera ↓↓↓

# 離陸
def takeoff():
        print("-----")
        try:
            sent = sock.sendto('takeoff'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 着陸
def land():
        print("land")
        try:
            sent = sock.sendto('land'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 上昇(20cm)
def up():
        try:
            sent = sock.sendto('up 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 下降(20cm)
def down():
        try:
            sent = sock.sendto('down 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 前に進む(5cm)
def forward():
        print("forward")
        try:
            sent = sock.sendto('forward 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 後に進む(5cm)
def back():
        print("back")
        try:
            sent = sock.sendto('back 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# 右に進む(20cm)
def right():
        print("right")
        try:
            sent = sock.sendto('right 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左に進む(20cm)
def left():
        print("left")
        try:
            sent = sock.sendto('left 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# 右回りに回転(5 deg)
def cw():
        print("cw")
        try:
            sent = sock.sendto('cw 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass
# 左回りに回転(5 deg)
def ccw():
        print("ccw")
        try:
            sent = sock.sendto('ccw 20'.encode(encoding="utf-8"), TELLO_ADDRESS)
        except:
            pass

# データ受け取り用の関数(thread処理をするので割り込みで行われる)
def udp_receiver():
    while True:
        try:
            response, _ = sock.recvfrom(1024)
        except Exception as e:
            print(e)
            break
"""
def move():
    if latest_data["id"] is not None:
        print("ARuco is detected")

        if latest_data["distance"]<100:
            back()
        elif latest_data["distance"]>160:
            forward()
        if latest_data["yaw"]>5:
            cw()
        elif latest_data["yaw"]<-5:
            ccw()
    else:
        print("cannot find ARuco")
"""
#実際のARマーカーの値を踏まえた制御
def move():
    while True:
        if push_b:  # bキーでON/OFF
            if latest_data["id"] is not None:
                print("ARuco is detected")

                if latest_data["distance"] < min_distance:
                    back()
                elif latest_data["distance"] > max_distance:
                    forward()

                if latest_data["yaw"] > max_degree:
                    cw()
                elif latest_data["yaw"] < min_degree:
                    ccw()

                if latest_data["x"] > max_xposition:
                     right()
                elif latest_data["x"] < min_xposition:
                     left()
            else:
                print("cannot find ARuco")
        time.sleep(0.1)  # 周期制御（100msごとに判定）

#各詳細データの読み取り用関数

def data_print():
    while True:
        #with data_lock:
        if latest_data["id"] is not None:
            print(f"[DATA] id={latest_data['id']} \n"
                    f"dist={latest_data['distance']:.2f} \n"
                    f"x={latest_data['x']:.1f} y={latest_data['y']:.1f} \n"
                    f"roll={latest_data['roll'] :.1f} pitch={latest_data['pitch']:.1f} yaw={latest_data['yaw']:.1f}\n")
        time.sleep(0.1)


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
threading.Thread(target=udp_receiver, daemon=True).start()
threading.Thread(target=data_print, daemon=True).start()
threading.Thread(target=move, daemon=True).start()



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
#↑↑↑End of capturing of tello images

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(
        gray_frame, marker_dict, parameters=param_markers
    )
    if marker_corners:
        rVec, tVec, _ = aruco.estimatePoseSingleMarkers(
            marker_corners, MARKER_SIZE, cam_mat, dist_coef
        )
        total_markers = range(0, marker_IDs.size)
        for ids, corners, i in zip(marker_IDs, marker_corners, total_markers):
            cv.polylines(
                frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA
            )
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

            # Calculating the distance
            distance = np.sqrt(
                tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2
            )
            # Draw the pose of the marker
            """
            point = cv.drawFrameAxes(frame, cam_mat, dist_coef, rVec[i], tVec[i], 4, 4)
            cv.putText(
                frame,
                f"id: {ids[0]} Dist: {round(distance, 2)}",
                top_right,
                cv.FONT_HERSHEY_PLAIN,
                1.3,
                (0, 0, 255),
                2,
                cv.LINE_AA,
            )
            cv.putText(
                frame,
                f"x:{round(tVec[i][0][0],1)} y: {round(tVec[i][0][1],1)} ",
                bottom_right,
                cv.FONT_HERSHEY_PLAIN,
                1.0,
                (0, 0, 255),
                2,
                cv.LINE_AA,
            )
            """
        # rVec[i] を回転行列に変換
        rotation_matrix, _ = cv.Rodrigues(rVec[i])
        
        # 回転行列からオイラー角を計算する
        sy = np.sqrt(rotation_matrix[0,0]**2 + rotation_matrix[1,0]**2)

        singular = sy < 1e-6
        if not singular:
            pitch  = np.arctan2(rotation_matrix[2,1], rotation_matrix[2,2])
            yaw = np.arctan2(-rotation_matrix[2,0], sy)
            roll   = np.arctan2(rotation_matrix[1,0], rotation_matrix[0,0])
        else:
            pitch  = np.arctan2(-rotation_matrix[1,2], rotation_matrix[1,1])
            yaw = np.arctan2(-rotation_matrix[2,0], sy)
            roll   = 0


        # --- 角度を度数法に変換 ---
        angles_deg = np.degrees([roll, pitch, yaw])
        """
        # --- カメラ映像に描画 ---
        cv.putText(frame, f"Roll: {angles_deg[0]:.1f}", (30, 60),
                    cv.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"Pitch: {angles_deg[1]:.1f}", (30, 80),
                    cv.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2, cv.LINE_AA)
        cv.putText(frame, f"Yaw: {angles_deg[2]:.1f}", (30, 100),
                    cv.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2, cv.LINE_AA)
        """
                # print(ids, "  ", corners)
        #データの更新
        #with data_lock:
        latest_data["id"] = ids[0]
        latest_data["distance"] = distance
        latest_data["x"] = tVec[i][0][0]
        latest_data["y"] = tVec[i][0][1]
        latest_data["roll"] = angles_deg[0]
        latest_data["pitch"] = angles_deg[1]
        latest_data["yaw"] = angles_deg[2]
        #QRがない場合は他の文字を代入
    else:
        latest_data["id"] = None
        latest_data["distance"] = 0.0
        latest_data["x"] = 0
        latest_data["y"] = 0
        latest_data["roll"] = 0
        latest_data["pitch"] = -180
        latest_data["yaw"] = 0
    # カメラ映像を画面に表示
    cv.imshow('Tello Camera View', frame)
    #停止コード    
    key = cv.waitKey(1)
    if key == ord("q"):
        break
        # jキーで離陸
    elif key == ord('j'):
        takeoff()
    # kキーで着陸
    elif key == ord('k'):
        land()
    # wキーで前進
    elif key == ord('w'):
        forward()
    # sキーで後進
    elif key == ord('s'):
        back()
        # hキーで上昇
    elif key == ord('h'):
        up()
        command_text = "Up"
    # lキーで下降
    elif key == ord('l'):
        down()
        command_text = "Down"
            #bキーで距離を測定して動く
    if key == ord('b'):
        if push_b == False:
            push_b = True
        else:
            push_b = False
    

land()
cap.release()
cv.destroyAllWindows()

# ビデオストリーミング停止
sock.sendto('streamoff'.encode('utf-8'), TELLO_ADDRESS)
