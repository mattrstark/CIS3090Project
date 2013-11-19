from PIL import Image
import time
import sys
import multiprocessing as mp
import logging
#logger = mp.log_to_stderr()
#logger.setLevel(mp.SUBDEBUG)


global assetDir
global saveDir
global ext
global procNum
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

def dither(image, pixelNum, threadID, procNum):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        #get the median RGB of neighbouring pixels
        for j in range(-1,2):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-1,2):
                    if((offY + k) > 0 and (offY + k) < height):
                        redValues.append(data[offX+j,offY+k][0])
                        greenValues.append(data[offX+j,offY+k][1])
                        blueValues.append(data[offX+j,offY+k][2])
                        newData[offX][offY] = (medianRed,medianGreen,medianBlue)
    return newData
    
# median function modified from http://stackoverflow.com/a/10482734
def median(mylist):
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2
    return sorts[length / 2]

def medianNoiseRemoval(image, pixelNum, threadID, procNum):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        redValues = []
        greenValues = []
        blueValues = []
        #get the median RGB of neighbouring pixels
        for j in range(-1,2):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-1,2):
                    if((offY + k) > 0 and (offY + k) < height):
                        redValues.append(data[offX+j,offY+k][0])
                        greenValues.append(data[offX+j,offY+k][1])
                        blueValues.append(data[offX+j,offY+k][2])
        medianRed = median(redValues)
        medianGreen = median(greenValues)
        medianBlue = median(blueValues)
        newData[offX][offY] = (medianRed,medianGreen,medianBlue)
    return newData

def threshold(image, pixelNum, threadID, procNum, secondValue):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    
    if(secondValue != 0):    
        thresholdValue = secondValue
    else:
        thresholdValue = 125
    
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        # if the green value is greater than the threshold value, make it white
        if(data[offX,offY][1] > thresholdValue):
            newData[offX][offY] = (255,255,255)
        else:
            newData[offX][offY] = (0,0,0)
        
    return newData

def blur(image, pixelNum, threadID, procNum, secondValue):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    
    # size of the blur kernel
    if(secondValue != 0):    
        blurSize = secondValue
    else:
        blurSize = 2
        
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        redValues = []
        greenValues = []
        blueValues = []
        #get the average RGB of all the pixels around each pixel
        for j in range(-blurSize,blurSize+1):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-blurSize,blurSize+1):
                    if((offY + k) > 0 and (offY + k) < height):
                        redValues.append(data[offX+j,offY+k][0])
                        greenValues.append(data[offX+j,offY+k][1])
                        blueValues.append(data[offX+j,offY+k][2])
        averageRed = sum(redValues) / len(redValues)
        averageGreen = sum(greenValues) / len(greenValues)
        averageBlue = sum(blueValues) / len(blueValues)
        newData[offX][offY] = (averageRed,averageGreen,averageBlue)
    return newData

def colourToGrey(image, pixelNum, threadID, procNum):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        # grey conversion by taking just the green value
        newData[offX][offY] = (data[offX,offY][1],data[offX,offY][1],data[offX,offY][1])
    return newData

def workerProc(threadID, imageName, algoToRun, secondValue, workload, procNum):
    print "~~~~~~~~~Worker #" + str(threadID) + " is starting~~~~~~~~~"
    image = Image.open(imageName).convert("RGB")
    if algoToRun == 0:
        newData = colourToGrey(image, workload, threadID, procNum)
    elif algoToRun == 1:
        newData = blur(image, workload, threadID, procNum, secondValue)
    elif algoToRun == 2:
        newData = threshold(image, workload, threadID, procNum, secondValue)
    elif algoToRun == 3:
        newData = medianNoiseRemoval(image, workload, threadID, procNum)
    
    returnValue = {'threadID' : threadID, 'newData' : newData, 'pixelAmount' : workload}
    #print "returned",threadID,workload
    return returnValue

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("Not enough arguments provided")

    startTime = time.time()
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
    
    if(width != width2 or height != height2):
        print "Image dimensions do not match"
        sys.exit()
    
    for i in range(0, width):
        for j in range(0, height):
            if(data[i, j] != data2[i, j]):
                print "pixel at",i,j,"does not match"
                sys.exit()
    print "images match"
    
    