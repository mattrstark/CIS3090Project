from PIL import Image
import time
import sys

global assetDir
global saveDir
global ext
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

argumentExample = "Expected args: <image_name> <image_name2> \n\
Example args: test.jpg out.jpg"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print argumentExample
        sys.exit("Not enough arguments provided")

    imageName = sys.argv[1]
    imageName2 = sys.argv[2]
    
    try:
        image = Image.open(imageName).convert("RGB")
    except IOError:
        sys.exit("Failed to open image: " + imageName);
    width, height = image.size
    try:
        image2 = Image.open(imageName2).convert("RGB")
    except IOError:
        sys.exit("Failed to open image: " + imageName2);
    width2, height2 = image2.size
    
    data = image.load()
    data2 = image2.load()
    
    # initial comparisons of widths and heights, if they don't match we know they're not equal
    if(width != width2 or height != height2):
        print "Image dimensions do not match"
        sys.exit()
    
    totalPixels = width * height
    pixelCount = 0

    # compare the amount of matching pixels
    for i in range(0, width):
        for j in range(0, height):
            if(data[i, j] != data2[i, j]):
                pixelCount += 1


    percentImageMatch = (float(totalPixels - pixelCount) / totalPixels) * 100
    print "Images are %.2f%% match." % percentImageMatch
    print  str(totalPixels - pixelCount) + "/" + str(totalPixels) + " pixels are the same."
    
    