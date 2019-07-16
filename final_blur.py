# -*- coding: utf-8 -*-
from  tkinter import *
from tkinter import filedialog
import os
from imageai.Detection import ObjectDetection
from PIL import Image, ImageDraw, ImageFilter
import piexif

class trans:
    def __init__(self,root):
        frame = Frame(root, bd= 5)
        frame.pack()
        s_var = StringVar()
        l = Label(frame, textvariable=s_var,bg='white', bd=5, width=40)
        b = Button(frame, text='select folder',height= 2, command= lambda: self.get_dir(s_var))
        b.pack()
        l.pack()
        frame_2 = Frame(root,height= 20,bd=5)
        frame_2.pack()
        frame_b =Frame(root)
        frame_b.pack()
        t = Text(frame_b,width= 40, height=10)
        t.pack()
        self.t = t
        Fotorun = Button(frame_2, text='block image', command=self.loop).grid(row=1, column=1)

    def get_dir(self,var):
        self.dir_name = filedialog.askdirectory()
        var.set(self.dir_name)
    def radius_calc(self,array):
        x0 = array[0]
        y0 = array[1]
        x1 = array[2]
        y1 = array[3]
        x_dis = x1 - x0
        y_dis = y1 - y0
        #print ('calculate size: {},{}'.format(x_dis,y_dis))
        if x_dis > 400 or y_dis > 400:
            return 10
        else:
            return 7
    def image_blur(self,img,target_path, detector):
        #  image detection
        img_dir = os.path.dirname(img)
        img_name = os.path.basename(img)
        img_num = os.path.splitext(img_name)
        print(img)

        detections = detector.detectObjectsFromImage(input_image=img, output_image_path='./temp/d-{}'.format(img_name))

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
                radius = self.radius_calc(array)
                #print (radius)
                blur = cropped.filter(ImageFilter.GaussianBlur(radius=radius))
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
        detector.setModelPath(r"C:\Users\Streckenkontrolle\Documents\liscensedetect/resnet50_coco_best_v2.0.1.h5")
        detector.loadModel()

        source = self.dir_name
        target = source + '_blocked'

        text = self.t
        i = 1
        try:
            os.mkdir(target)
            print('{} created'.format(target))
            text.insert(END,'{} created \n'.format(target))
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
                print (i)
                i+=1
                full_path = os.path.join(root, file)
                target_path = full_path.replace(source, target)
                if os.path.isfile(target_path) is False:
                    if 'jpg' in file.lower() or 'png' in file.lower():
                        text.insert(END,target_path)
                        self.image_blur(full_path, target_path,detector)
                else:
                    print('{} existed'.format(full_path))
                    text.insert(END,'{} existed\n'.format(file))


def main():
    root = Tk()
    root.title('image blocker')
    root.geometry('470x305')
    trans(root)
    root.mainloop()

if __name__ == '__main__':
    main()
