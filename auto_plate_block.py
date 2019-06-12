import os
from os import environ
from openalpr import Alpr
from imageai.Detection import ObjectDetection
from PIL import Image, ImageDraw

def plate_detector(img):
    #  load alpr
    alpr_dir = r'D:\openalpr-2.3.0-win-64bit\openalpr_64'
    environ['PATH'] = alpr_dir + ';' + environ['PATH']

    alpr = Alpr('eu', alpr_dir + '/openalpr.conf', alpr_dir + '/runtime_data')
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)

    #  image detection
    img_dir = os.path.dirname(img)
    img_name = os.path.basename(img)
    print (img_dir,img_name)

    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image=img, output_image_path=os.path.join(img_dir,'d-{}'.format(img_name)))

    #  open image
    imageObject = Image.open(img)
    image_draw = ImageDraw.Draw(imageObject)

    i=1

    #  find all plates
    for eachObject in detections:
        if eachObject["name"] in ('car', 'bus'):
            # print(eachObject['name'])
            array = eachObject["box_points"]
            x0 = array[0]
            y0 = array[1]
            # print (x0,y0)
            jpg = "./temp/{}.jpg".format(i)
            cropped = imageObject.crop(array)
            cropped.save(jpg)
            new_h = 500
            i_img = Image.open(jpg)
            H_percent = (new_h / float(i_img.size[1]))
            img_width = int(float(i_img.size[0]) * float(H_percent))
            r_i_jpg = img.resize((img_width, new_h), Image.ANTIALIAS)
            r_i_jpg.save(jpg)
            i += 1
            results = alpr.recognize_file(jpg)
            if not results['results']:
                print('no plates found')

            else:
                # print (results)
                for plate in results['results']:
                    # print (plate)
                    x_cord = [roi['x'] for roi in plate['coordinates']]
                    y_cord = [roi['y'] for roi in plate['coordinates']]

                    ymax, ymin = y0 + max(y_cord) / H_percent, y0 + min(y_cord) / H_percent
                    xmax, xmin = x0 + max(x_cord) / H_percent, x0 + min(x_cord) / H_percent
                    # print (ymin,ymax,xmin,xmax)
                    image_draw.rectangle((xmin, ymax, xmax, ymin), fill='black')
        else:
            print(eachObject['name'] + ' is not vehicle')

    imageObject.save('{}-b.jpg'.format(img_name))

def main():
    img = r'C:\Users\Streckenkontrolle\Documents\liscensedetect\foto\DSC_2969.JPG'
    plate_detector(img)



if __name__ == '__main__':
    main()