CIS3090Project
==============

# piltest.py

The expected args for piltest.py is: <image_name> <CPUs> <algorithm> (arg)

Example arguments: test.jpg 4 1 2

image_name: name of the image to perform the algorithm on (found inside the assets folder)

CPUs: number of cores to use

algorithm: integer value to tell which algorithm to perform

    0: greyscale
    
    1: blur
    
    2: threshold
    
    3: median noise removal
    
    4: dilation
    
    5: erosion
    
arg: optional argument for the specified algorithms

    blur: amount of pixels around each pixel to take the average of. (defaults to 2)
    
    threshold: value between 0-255 (defaults to 125). Any pixel’s green value below this value will be set to black, and any above it is set to white.
    
After successfully running piltest.py the resulting image can be located under “results\out.jpg”.

# imagecompare.py

The expected args for imagecompare.py is: <first_image_name> <second _image_name>

Example arguments: output1.jpg output2.jpg

first_image_name: name of the first image to run the comparison on

second_image_name: name of the second image to run the comparison on
