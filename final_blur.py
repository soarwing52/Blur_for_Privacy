# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
import os
from imageai.Detection import ObjectDetection
from PIL import Image, ImageDraw, ImageFilter
import piexif
import shutil
import threading


class trans:
    def __init__(self, root):
        frame = Frame(root, bd=5)
        frame.pack()
        s_var = StringVar()
        l = Label(frame, textvariable=s_var, bg='white', bd=5, width=40)
        b = Button(frame, text='select folder', height=2, command=lambda: self.get_dir(s_var))
        b.pack()
        l.pack()

        frame_2 = Frame(root, height=20, bd=5)
        frame_2.pack()
        Fotorun = Button(frame_2, text='block image', command=self.open_thread).grid(row=1, column=1)


        frame_b = Frame(root)
        frame_b.pack()
        self.current = StringVar()
        current_label = Label(frame_b,textvariable=self.current,bd=5,bg='white',width=80).pack()
        t = Text(frame_b,bd=10)
        t.pack()
        self.t = t


    def get_dir(self, var):
        self.dir_name = filedialog.askdirectory()
        var.set(self.dir_name)

    def image_blur(self, img, target_path, detector):
        #  image detection
        img_dir = os.path.dirname(img)
        img_name = os.path.basename(img)
        img_num = os.path.splitext(img_name)
        print(img)

        try:
            detections = detector.detectObjectsFromImage(input_image=img,
                                                         output_image_path='./temp/d-{}'.format(img_name))
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

    def loop(self):

        detector = ObjectDetection()
        detector.setModelTypeAsRetinaNet()
        detector.setModelPath(r"./resnet50_coco_best_v2.0.1.h5")
        detector.loadModel()

        source = self.dir_name
        target = source + '_blocked'

        text = self.t
        i = 1
        try:
            os.mkdir(target)
            print('{} created'.format(target))
            #text.insert(END, '{} created \n'.format(target))
        except FileExistsError:
            pass
        finally:
            pass

        for root, dirs, files in os.walk(source):
            for dir in dirs:
                full = os.path.join(root, dir)
                target_dir = full.replace(source, target)
                try:
                    os.mkdir(target_dir)
                except FileExistsError:
                    pass
                finally:
                    pass

            for file in files:
                if 'jpg' in file.lower() or 'png' in file.lower():
                    print (i)
                    i += 1
                    full_path = os.path.join(root, file)
                    target_path = full_path.replace(source, target)
                    if os.path.isfile(target_path) is False:
                        self.current.set(target_path)
                        #text.insert(END, target_path + '\n')
                        try:
                            self.image_blur(full_path, target_path, detector)
                        except OSError:
                            text.insert(END,target_path)
                            print ('image broken')
                        except ValueError:
                            text.insert(END, target_path)
                            print ('value')
                        except IOError:
                            text.insert(END, target_path)
                            print('IO')

                    else:
                        print('{} existed'.format(full_path))
                        self.current.set('{} existed \n'.format(file))
                        #text.insert(END, '{} existed \n'.format(file))
                else:
                    print (file + ' is not a picture')

    def open_thread(self):
        T1 = threading.Thread(target=self.loop,name='T1')
        T1.start()



def main():
    if not os.path.isdir('temp'):
        os.mkdir('temp')
    root = Tk()
    root.title('image blocker')
    root.geometry('470x305')
    trans(root)
    root.mainloop()
    shutil.rmtree('temp')
    os._exit(0)


if __name__ == '__main__':
    main()
