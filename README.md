## auto-plate-block
automatic block out the driving plates in the picture

this project combines two library I found

ImageAI for object detection from OlafenwaMoses
https://github.com/OlafenwaMoses/ImageAI

and openalpr for plate recognition

## Objective
to censor people and car plates for privacy issues

#The final result
The openalpr is eventually not used for the limitations of recognition

and also this script didn't need to read the plates, just need to make it unreadable.

So the final method is to pick out the location of Person, Car, Truck and apply GaussianBlur 

with closer/bigger objects I apply level 7 and further/smaller 11

## Usage
simply select the directory containing the images, and it will create a _foldername_blocked next to it

I didn't apply threading in this tool so the main GUI will freeze.
