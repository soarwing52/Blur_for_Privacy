import os
from imageai.Detection import ObjectDetection
from PIL import Image, ImageDraw, ImageFilter
import piexif

def image_blur(img):
    #  image detection
    img_dir = os.path.dirname(img)
    img_name = os.path.basename(img)
    img_num = os.path.splitext(img_name)
    print (img_name)

    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath( r"C:\Users\Streckenkontrolle\Documents\liscensedetect/resnet50_coco_best_v2.0.1.h5")
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image=img, output_image_path='./temp/d-{}'.format(img_name))

    #  open image
    imageObject = Image.open(img)
    image_draw = ImageDraw.Draw(imageObject)

    for eachObject in detections:
        if eachObject["name"] in ('car', 'bus','truck','person'):
            print(eachObject['name'])
            array = eachObject["box_points"]
            x0 = array[0]
            y0 = array[1]
            # print (x0,y0)
            cropped = imageObject.crop(array)
            blur = cropped.filter(ImageFilter.GaussianBlur(radius=5))
            imageObject.paste(blur,array)
        else:
            print(eachObject['name'] + ' is not vehicle')


    des_img =r'X:/Loehne/dkblock/{}'.format(img_name)
    imageObject.save(des_img)
    piexif.transplant(img,des_img)


def main():
    pass

if __name__ == '__main__':
    name = r'X:\Loehne\blocked\DSC_2880.JPG'
    image_blur(name)