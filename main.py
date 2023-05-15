import sys
import cv2
import imutils
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import threading
import winsound
import argparse

class App(QtWidgets.QMainWindow):
        
    def __init__(self):
        super().__init__()
        self.title = 'Intrusion Detection System ver 1.0.0'
        self.left =50
        self.top = 50
        self.width = 1280
        self.height = 720
        self.roi_defined = False
        self.poly_points_list = []
        self.initUI()
        self.first_frame = None
        self.motion_detected = False
        self.motion_start_time = None
        self.start_time = time.time()
        self.first_frame_time = time.time()
        self.line_color = (0,255,0)
              

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.image_label = QtWidgets.QLabel(self.centralwidget)
        self.image_label.setGeometry(QtCore.QRect(0, 0, self.width, self.height))
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

        self.show()
    
    def beep_audio(self):
        self.freq = 2500
        self.duration = 300
        winsound.Beep(self.freq, self.duration)


    def update_frame(self):
                
        ret, image = self.cap.read()
        if ret:
            # fps = self.cap.get(cv2.CAP_PROP_FPS)
            # cv2.putText(image,f'{fps} FPS',(50,50),cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0),2)

            original_image = image.copy()  # make a copy of the original image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if self.roi_defined:
                mask = np.zeros(image.shape[:2], dtype=np.uint8)
                
                for index, poly_points in enumerate(self.poly_points_list):
                    roi_corners = np.array([poly_points], dtype=np.int32)
                    channel_count = image.shape[2]
                    ignore_mask_color = (255,) * channel_count
                    cv2.fillPoly(mask, roi_corners, ignore_mask_color,lineType=cv2.LINE_4)
                    if self.motion_detected:
                        self.line_color = (255,0,0)
                    else:
                        self.line_color = (0,255,0)
                    image = cv2.polylines(image, [roi_corners], True, self.line_color, 2)
                    
                    # apply the mask to the original image
                    masked_image = cv2.bitwise_and(original_image, original_image, mask=mask)

                    gray  = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
                    gray = cv2.GaussianBlur(gray,(21,21),0)
                    
                    # update first frame every 1 minutes
                    if (self.first_frame is None and time.time() - self.start_time > 10 ) or (time.time() - self.first_frame_time > 60  and self.motion_detected == False):
                        self.first_frame = gray
                        cv2.imshow("reference frame", self.first_frame)
                        self.first_frame_time = time.time()
                    try:
                        delta_frame = cv2.absdiff(self.first_frame,gray)
                        threshold_frame = cv2.threshold(delta_frame,50,255,cv2.THRESH_BINARY)[1]
                        threshold_frame = cv2.dilate(threshold_frame, None, iterations = 2)
                        cv2.imshow("current frame",threshold_frame)
                        (cntr, _) = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        
                        # check for motion detection
                        if not self.motion_detected:
                            for contour in cntr:
                                # print("contour", len(contour))
                                if cv2.contourArea(contour) > 50:
                                    continue
                                (x,y,w,h) = cv2.boundingRect(contour)
                                cv2.rectangle(masked_image,(x,y),(x+w,y+h),(0,255,0),3)
                                
                                self.motion_detected = True
                                self.motion_start_time = time.time()
                                break
                        else:
                            if not cntr:
                                self.motion_detected = False
                            elif time.time() - self.motion_start_time > 1:
                                # raise alarm
                                cv2.putText(image, "Intrusion Detected!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)  
                                threading.Thread(target=self.beep_audio).start()

                    except:
                        continue         

            image = imutils.resize(image, width=self.width)
            h, w, ch = image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(convert_to_Qt_format)
            self.image_label.setPixmap(pixmap)

    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if not self.roi_defined:
                self.poly_points_list = []
                self.roi_defined = True
                self.first_frame = None  # Reset the first frame
                self.motion_detected = False  # Reset motion detection
                self.motion_start_time = None
                self.start_time = time.time()
                self.first_frame_time = time.time()
            x, y = event.x(), event.y()
            self.poly_points_list.append([[x, y]])
            self.update()
        elif event.button() == QtCore.Qt.RightButton:
            if self.roi_defined:
                self.poly_points_list.pop()
                self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.roi_defined = False
            self.poly_points_list = []
            self.first_frame = None  # Reset the first frame
            self.motion_detected = False  # Reset motion detection
            self.motion_start_time = None
            self.start_time = time.time()
            self.first_frame_time = time.time()
            self.update()


    def mouseMoveEvent(self, event):
        if self.roi_defined:
            x, y = event.x(), event.y()
            self.poly_points_list[-1].append([x, y])
            self.update()

    def paintEvent(self, event):
        if self.roi_defined:
            painter = QtGui.QPainter(self)
            pen = QtGui.QPen(QtGui.QColor(255, 0, 0), 2, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            for poly_points in self.poly_points_list:
                poly = QtGui.QPolygonF([QtCore.QPointF(*point) for point in poly_points])
                painter.drawPolygon(poly)

    
    def closeEvent(self, event):
        self.cap.release()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--feed", required=True, help="Enter the camera or video path")
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.cap = cv2.VideoCapture(args.feed)
    sys.exit(app.exec_())
