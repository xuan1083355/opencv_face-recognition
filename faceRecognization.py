from PyQt6 import QtWidgets
from PyQt6.QtGui import QImage, QPixmap
import sys, cv2, threading

#建立視窗
app=QtWidgets.QApplication(sys.argv)
window_h=600
window_w=550
scale=0.85 #影片高度的比例

form=QtWidgets.QWidget()
form.setWindowTitle('A1083355_Final_Report')
form.resize(window_w,window_h)
form.setStyleSheet('background:#f0f8ff;')

#元件(標籤、按鈕)
label=QtWidgets.QLabel(form)
label.setGeometry(0,0,window_w,int(window_w*scale))

btn1=QtWidgets.QPushButton(form)
btn1.setGeometry(10,window_h-50,70,40)
btn1.setText('拍照')
btn1.setStyleSheet('''
    QPushButton{
        background:#fffacd;
        color:#000080;
        font-size:20px;
        border:2px solid #000;
    
    }
    QPushButton:hover{
        background:#000080;
        color: #fffacd;
        
    }
    
''')

photo=False
#按下拍照鈕的動作
def takephoto():
    global photo
    photo=True
    
btn1.clicked.connect(takephoto)


btn2=QtWidgets.QPushButton(form)
btn2.setGeometry(80,window_h-50,70,40)
btn2.setText('錄影')
btn2.setStyleSheet('''
    QPushButton{
        background:#fffacd;
        color:#000080;
        font-size:20px;
        border:2px solid #000;
    
    }
    QPushButton:hover{
        background:#000080;
        color: #fffacd;
        
    }
    
''')

btn3=QtWidgets.QPushButton(form)
btn3.setGeometry(300,window_h-50,70,40)
btn3.setText('馬賽克')
btn3.setStyleSheet('''
    QPushButton{
        background:#fffacd;
        color:#000080;
        font-size:20px;
        border:2px solid #000;
    
    }
    QPushButton:hover{
        background:#000080;
        color: #fffacd;
        
    }
    
''')

# 啟用 OpenCV 的參考變數，預設 True  
#搭配一個全域變數(ocv)控制關閉的事件(當 PyQt6 視窗關閉時，同時也將 OpenCV 的迴圈停止，避免仍然在背景運作的狀況。)
ocv=True
# 關閉視窗時的動作
def closeOpenCV(self):
    global ocv,output
    ocv=False
    try:
        output.release()  
    except:
        pass
form.closeEvent=closeOpenCV

# 視窗尺寸改變時的動作
def windowResize(self):
    global window_w, window_h, scale
    window_w = form.width()                 # 取得視窗寬度
    window_h = form.height()                # 取得視窗高度
    label.setGeometry(0,0,window_w,int(window_w*scale))  # 設定 QLabel 尺寸
    btn1.setGeometry(10,window_h-50,70,40)  # 設定按鈕位置
    btn2.setGeometry(80,window_h-50,70,40) # 設定按鈕位置
    btn3.setGeometry(350,window_h-50,70,40) # 設定按鈕位置
form.resizeEvent = windowResize             # 視窗尺寸改變時觸發



#錄影
fourcc=cv2.VideoWriter_fourcc(*'mp4v')
recordState=False
#按下錄影鈕
def recordVideo():
    global recordState, output
    if recordState==False:  # 如果按下按鈕時沒有在錄影
        output=cv2.VideoWriter('output.mp4',fourcc,20.0,(window_w,int(window_w*scale)))
        recordState=True
        btn2.setGeometry(80,window_h-50,250,40)  # 因為內容文字變多，改變尺寸
        btn2.setText('錄影中，點擊停止並存擋')
    else: # 如果按下按鈕時正在錄影，儲存影片，釋放資源
        recordState=False
        output.release()
        btn2.setGeometry(80,window_h-50,70,40)   # 改變尺寸
        btn2.setText('錄影')

btn2.clicked.connect(recordVideo)

#馬賽克
mos=False
def mosaic():
    global mos
    if mos==True:
        mos=False
        btn3.setGeometry(350,window_h-50,70,40)      # 設定拍照鈕的位置和尺寸
        btn3.setText('馬賽克')
    else:  #使用馬賽克效果
        mos=True
        btn3.setGeometry(350,window_h-50,180,40)   # 改變尺寸
        btn3.setText('取消馬賽克')

btn3.clicked.connect(mosaic)

#開啟攝影機
def opencv():
    global photo,output,recordState,mos,window_h,window_w,scale

    cap=cv2.VideoCapture(0) #開啟攝影機
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while ocv:
        ret,frame=cap.read()
        if not ret:
            print("Cannot receive frame")
            break
        
        frame = cv2.resize(frame, (window_w, int(window_w*scale)))  # 改變尺寸符合視窗
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # 影像轉灰階，較好進行人臉辨識
        
        #若馬賽克放下面，不會被錄影進去(因程式為由上而下執行)
        
        if mos==True: 
            face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(gray)      # 偵測人臉
            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]
                level = 15 #馬賽克程度
                mh = int(h/level)
                mw = int(w/level)
                face = cv2.resize(face, (50, 50))  # 調整馬賽克塊大小
                face = cv2.resize(face, (mw,mh), interpolation=cv2.INTER_LINEAR)
                face = cv2.resize(face, (w,h), interpolation=cv2.INTER_NEAREST)
                frame[y:y+h, x:x+w] = face  

        if photo==True:
            photo=False
            cv2.imwrite('A1083355.jpg',frame)

        if recordState==True:
            output.write(frame) # 按下錄影時，將檔案儲存到 output

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 改為 RGB(OpenCV 讀取的影像色彩為 BGR，必須先轉換成 RGB，再使用 PyQt6 的 QImage 讀取，才能在視窗中正常顯示。)
        height, width, channel = frame.shape  # 讀取尺寸和 channel數量
        bytesPerline = channel * width  # 設定 bytesPerline ( 轉換使用 )
        # 轉換影像為 QImage，讓 PyQt6 可以讀取
        img = QImage(frame, width, height, bytesPerline, QImage.Format.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(img))  # QLabel 顯示影像
        

video = threading.Thread(target=opencv)     # 將 OpenCV 的部分放入 threading 裡執行
video.start()

form.show()
sys.exit(app.exec())
        
