from PyQt6.QtWidgets import (QMainWindow, QPushButton, QLabel, QFileDialog, QApplication)
import cv2
import numpy
import winsound
import sys

class Panorama(QMainWindow) :
    def __init__(self) :
        super().__init__()
        self.setWindowTitle("파노라마 영상")
        self.setGeometry(200,200,700,200)

        collectButton=QPushButton("영상 수집",self)
        self.showButton=QPushButton("영상 보기",self)
        self.stitchButton=QPushButton("봉합",self)
        self.colortograyButton=QPushButton("흑백 변환",self)
        self.saveButton=QPushButton("저장",self)
        quitButton=QPushButton('나가기',self)
        self.label=QLabel("환영합니다!",self)

        collectButton.setGeometry(10,25,100,30)
        self.showButton.setGeometry(110,25,100,30)
        self.stitchButton.setGeometry(210,25,100,30)
        self.colortograyButton.setGeometry(310,25,100,30)
        self.saveButton.setGeometry(410,25,100,30)
        quitButton.setGeometry(550,25,100,30)
        self.label.setGeometry(10,70,600,170)

        # 영상보기, 통합, 흑백변환, 저장 버튼 비활성으로 초기화
        self.showButton.setEnabled(False)
        self.stitchButton.setEnabled(False)
        self.colortograyButton.setEnabled(False)
        self.saveButton.setEnabled(False)

        collectButton.clicked.connect(self.collectFunction)
        self.showButton.clicked.connect(self.showFunction)
        self.stitchButton.clicked.connect(self.stitchFunction)
        self.colortograyButton.clicked.connect(self.colortograyFunction)
        self.saveButton.clicked.connect(self.saveFunction)
        quitButton.clicked.connect(self.quitFunction)

    def collectFunction(self):
        # 다시 시도하는 경우를 대비하여 다시 비활성으로 초기화
        self.showButton.setEnabled(False)
        self.stitchButton.setEnabled(False)
        self.colortograyButton.setEnabled(False)
        self.saveButton.setEnabled(False)

        self.label.setText("c를 여러 번 눌러 수집하고 끝나면 q를 눌러 비디오를 끕니다.")

        self.cap=cv2.VideoCapture(0,cv2.CAP_DSHOW)
        if not self.cap.isOpened(): sys.exit("카메라 연결 실패")

        self.imgs=[]
        while True :
            ret, frame = self.cap.read()
            if not ret : break
        
            cv2.imshow("video display", frame)

            key = cv2.waitKey(1)
            if key == ord("c") :
                self.imgs.append(frame) #영상 저장
            
            elif key == ord("q") :
                self.cap.release()
                cv2.destroyWindow("video display")
                break

        if len(self.imgs) >= 2:
            self.showButton.setEnabled(True)
            self.stitchButton.setEnabled(True)
            self.saveButton.setEnabled(True)

    def showFunction(self):
        self.label.setText("수집된 영상은 "+str(len(self.imgs))+"장입니다.")
        stack=cv2.resize(self.imgs[0], dsize=(0,0), fx=0.25, fy=0.25)
        for i in range(1, len(self.imgs)):
            stack=numpy.hstack((stack, cv2.resize(self.imgs[i], dsize=(0,0), fx=0.25, fy=0.25)))
        cv2.imshow("Image collection",stack)

    def stitchFunction(self) :
        stitcher=cv2.Stitcher_create()
        status, self.img_stitched=stitcher.stitch(self.imgs)
        if status == cv2.STITCHER_OK :
            cv2.imshow("Image stitched panorama", self.img_stitched)
            self.colortograyButton.setEnabled(True)
            self.label.setText("파노라마 제작에 성공했습니다.")
        else:
            winsound.Beep(3000,500)
            self.label.setText("파노라마 제작에 실패했습니다. 다시 시도하세요.")
        
    def colortograyFunction(self) :
        self.img_stitched_gray=cv2.cvtColor(self.img_stitched,cv2.COLOR_BGR2GRAY)
        self.img_stitched=self.img_stitched_gray
        cv2.imshow("Image(Grayscale)", self.img_stitched)

    def saveFunction(self):
        fname=QFileDialog.getSaveFileName(self,"파일 저장","./outputs/")
        
        cv2.imwrite(fname[0],self.img_stitched)
        self.label.setText("파노라마가 저장되었습니다.")

    def quitFunction(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.close()

app=QApplication(sys.argv)
win=Panorama()
win.show()
app.exec()