import sys, time
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog
from photoblur_ui import Ui_MainWindow

import os
from imageai.Detection import ObjectDetection
from PIL import Image, ImageDraw, ImageFilter
import piexif
import shutil

RUNNING = False

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.prj_dir = None
        self.t_jpg = BlurThread()
        self.btn_select_dir.clicked.connect(lambda: self.get_prjdir_dialog())
        self.btn_start.clicked.connect(lambda : self.start_thread())

        self.msg = QtWidgets.QMessageBox()
        self.msg.setWindowTitle('Warning')
        self.msg.setIcon(QtWidgets.QMessageBox.Information)

    def get_prjdir_dialog(self):
        self.prj_dir = QFileDialog.getExistingDirectory()
        self.project_label.setText(self.prj_dir)
        self.project_label.adjustSize()

    def start_thread(self):
        if not RUNNING:
            self.t_jpg.set_dir(self.prj_dir)
            self.t_jpg.start()
            self.t_jpg.update_progressbar.connect(self.update_progressbar)
            self.t_jpg.msg.connect(self.message_reciever)
        else:
            self.msg.setText('still blurring JPG')
            self.msg.exec_()

    def update_progressbar(self, val):
        self.progressBar.setValue(val)

    def message_reciever(self, msg):
        print(msg)
        if 'Error' in msg or 'fertig' in msg:
            self.textBrowser.append(msg)
        self.statusbar.showMessage(msg)


class BlurThread(QThread):
    update_progressbar = pyqtSignal(float)
    msg = pyqtSignal(str)
    def __int__(self, parent=None):
        super(BlurThread, self).__init__(parent)
        self.prj_dir = None

    def run(self):
        global RUNNING
        RUNNING = True
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(r"./resnet50_coco_best_v2.0.1.h5")
        self.detector.loadModel()
        if not os.path.isdir('temp'):
            os.mkdir('temp')

        source = self.prj_dir
        target = source + '_blocked'

        if not os.path.isdir(target):
            os.mkdir(target)
        total = len([1 for root,dirs,files in os.walk(source) for file in files if 'jpg' in file.lower() or 'png' in file.lower()])
        current = 0

        for root, dirs, files in os.walk(source):
            for folder in dirs:
                full_path = os.path.join(root, folder)
                target_dir = full_path.replace(source, target)
                if not os.path.isdir(target_dir):
                    os.mkdir(target_dir)


            for file in files:
                if 'jpg' in file.lower() or 'png' in file.lower():
                    full_path = os.path.join(root, file)
                    target_path = full_path.replace(source, target)
                    if os.path.isfile(target_path) is False:
                        self.msg.emit(full_path)
                        try:
                            self.image_blur(full_path, target_path)
                        except:
                            self.msg.emit('Error: {} broken image'.format(file))
                            print('image broken')
                    else:
                        print('{} existed'.format(full_path))
                        #self.current.set('{} existed \n'.format(file))
                else:
                    self.msg.emit(file + ' is not a picture')
                current += 1
                self.update_progressbar.emit(current * 100 / total)

        self.msg.emit('Blur fertig')
        self.update_progressbar.emit(100)
        RUNNING = False
        shutil.rmtree('temp')

    def set_dir(self,stt):
        self.prj_dir = stt

    def image_blur(self, img, target_path):
        #  image detection
        img_name = os.path.basename(img)

        try:
            detections = self.detector.detectObjectsFromImage(
                input_image=img, output_image_path='./temp/d-{}'.format(img_name))
        finally:
            pass

        #  open image
        imageObject = Image.open(img)
        image_draw = ImageDraw.Draw(imageObject)

        for eachObject in detections:
            if eachObject["name"] in ('car', 'bus', 'truck', 'motorcycle', 'person'):
                print(eachObject['name'])
                array = eachObject["box_points"]
                x0 = array[0]
                y0 = array[1]
                # print (x0,y0)
                cropped = imageObject.crop(array)
                blur = cropped.filter(ImageFilter.GaussianBlur(radius=7))
                imageObject.paste(blur, array)
            else:
                print(eachObject['name'] + ' is not vehicle')

        des_img = target_path
        imageObject.save(des_img)
        try:
            piexif.transplant(img, des_img)
        except ValueError:
            pass
        finally:
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())