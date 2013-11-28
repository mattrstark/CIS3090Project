from PIL import Image
import time
import sys
import multiprocessing as mp
import logging
#logger = mp.log_to_stderr()
#logger.setLevel(mp.SUBDEBUG)

global assetDir
global saveDir
assetDir = "assets/"
saveDir = "results/"

argumentExample = "Expected args: <image_name> <CPUs to use> <algorithm> (arg)\n\
Example args: test.jpg 4 1 2"

def erosion(image, pixelNum, threadID, procNum):
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
        # using lowest green since it's a good measurement of value
        lowestRed = 255
        lowestGreen = 255
        lowestBlue = 255
        # get the lowest value of neighbouring pixels
        for j in range(-1,2):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-1,2):
                    if((offY + k) > 0 and (offY + k) < height): 
                        if(data[offX+j,offY+k][1] < lowestGreen): 
                            lowestRed = data[offX+j,offY+k][0]
                            lowestGreen = data[offX+j,offY+k][1]
                            lowestBlue = data[offX+j,offY+k][2]
        newData[offX][offY] = (lowestRed,lowestGreen,lowestBlue)
    return newData

def dilation(image, pixelNum, threadID, procNum):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    # get any extra pixels if this processor is the last processor
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        # using highest green since it's a good measurement of value
        highestRed = 0
        highestGreen = 0
        highestBlue = 0
        # get the highest value of neighbouring pixels
        for j in range(-1,2):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-1,2):
                    if((offY + k) > 0 and (offY + k) < height): 
                        if(data[offX+j,offY+k][1] > highestGreen): 
                            highestRed = data[offX+j,offY+k][0]
                            highestGreen = data[offX+j,offY+k][1]
                            highestBlue = data[offX+j,offY+k][2]
        newData[offX][offY] = (highestRed,highestGreen,highestBlue)
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
    
    # get any extra pixels if this processor is the last processor
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
    
    # get any extra pixels if this processor is the last processor
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
    
    # get any extra pixels if this processor is the last processor
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
    
    # get any extra pixels if this processor is the last processor
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
    # determine which algorithm to run
    if algoToRun == 0:
        newData = colourToGrey(image, workload, threadID, procNum)
    elif algoToRun == 1:
        newData = blur(image, workload, threadID, procNum, secondValue)
    elif algoToRun == 2:
        newData = threshold(image, workload, threadID, procNum, secondValue)
    elif algoToRun == 3:
        newData = medianNoiseRemoval(image, workload, threadID, procNum)
    elif algoToRun == 4:    
        newData = dilation(image, workload, threadID, procNum)
    elif algoToRun == 5:    
        newData = erosion(image, workload, threadID, procNum)
    else:
        print "Unrecognized algorithm argument"
    
    returnValue = {'threadID' : threadID, 'newData' : newData, 'pixelAmount' : workload}
    #print "returned",threadID,workload
    return returnValue

# combine the modified image chunks into one final image
def log_result(returnedValue):
    global modifiedImage
    threadID = returnedValue['threadID']
    returnedData = returnedValue['newData']
    pixelNum = returnedValue['pixelAmount']
    print "~~~~~~~~Worker #" + str(threadID) + " is done~~~~~~~"
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        modifiedImage[offX,offY] = returnedData[offX][offY]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print argumentExample
        sys.exit("Not enough arguments provided")
    try:
        procNum = int(sys.argv[2])
    except ValueError:
        print argumentExample
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not a valid number")

    if not (99 > procNum > 0):
        print argumentExample
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not between a valid range of 1 and 99")    

    secondaryArgument = 0

    if len(sys.argv) < 4:
        algorithmToDo = 0
    else:
        if(len(sys.argv) == 5):
            try:
                algorithmToDo = int(sys.argv[3])
                secondaryArgument = int(sys.argv[4])
            except ValueError:
                sys.exit("Argument 3: '" + sys.argv[3] + "' (algorithmToDo) or Argument 4: '" + sys.argv[4] + "'is not a valid number")
        else:
            try:
                algorithmToDo = int(sys.argv[3])
            except ValueError:
                sys.exit("Argument 3: '" + sys.argv[3] + "' (algorithmToDo) is not a valid number")

    startTime = time.time()
    imageName = assetDir + sys.argv[1]
    
    try:
        # open the image and convert it to a RGB format
        image = Image.open(imageName).convert("RGB")
    except IOError:
        sys.exit("Failed to open image: " + imageName);
    width, height = image.size
    area = width * height
    # calculate the pixel amount each section will get
    pixelAmount = area // procNum
    newImage = Image.new('RGB', image.size, (0,255,255))
    modifiedImage = newImage.load()
    
    # assign a pixel amount to each process
    pool = mp.Pool(procNum)
    for i in range(procNum):
        finalPixelAmount = pixelAmount
        print "~~~~~~~~Worker #" + str(i) + " is being assigned~~~~~~~"
        pool.apply_async(workerProc, args = (i, imageName, algorithmToDo, secondaryArgument, finalPixelAmount, procNum ), callback = log_result)

    pool.close()
    pool.join()
    
    elapsedTime = (time.time() - startTime)
    print "Done in %.4f seconds" % elapsedTime
    newImage.save(saveDir + "out.jpg")