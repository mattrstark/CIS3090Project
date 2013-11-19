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


def threshold(image, pixelNum, threadID, procNum):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    
    if(threadID == procNum - 1):
        area = width * height
        extraPixels = area % procNum
        pixelNum += extraPixels
        
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

def blur(image, pixelNum, threadID, procNum):
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
    blurSize = 2;
        
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        redValues = []
        greenValues = []
        blueValues = []
        #get the average RGB of all the pixels around each pixel
        for j in range(-blurSize,blurSize):
            if((offX + j) > 0 and (offX + j) < width):
                for k in range(-blurSize,blurSize):
                    if((offY + k) > 0 and (offY + k) < height):
                        redValues.append(data[offX+j,offY+k][0])
                        greenValues.append(data[offX+j,offY+k][1])
                        blueValues.append(data[offX+j,offY+k][2])
        averageRed = sum(redValues) / len(redValues)
        averageGreen = sum(greenValues) / len(greenValues)
        averageBlue = sum(blueValues) / len(blueValues)
        # grey conversion by taking just the green value
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

def workerProc(threadID, imageName, algoToRun, workload, procNum):
    print "~~~~~~~~~Worker #" + str(threadID) + " is starting~~~~~~~~~"
    image = Image.open(imageName).convert("RGB")
    if algoToRun == 0:
        newData = colourToGrey(image, workload, threadID, procNum)
    elif algoToRun == 1:
        newData = blur(image, workload, threadID, procNum)
    elif algoToRun == 2:
        newData = threshold(image, workload, threadID, procNum)
    elif algoToRun == 3:
        print "n is a prime number\n"
    
    returnValue = {'threadID' : threadID, 'newData' : newData, 'pixelAmount' : workload}
    #print "returned",threadID,workload
    return returnValue


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
        sys.exit("Not enough arguments provided")
    try:
        procNum = int(sys.argv[2])
    except ValueError:
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not a valid number")

    if not (99 > procNum > 1):
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not between a valid range of 1 and 99")    
    time.clock
    
    imageName = assetDir + sys.argv[1]
    
    try:
        image = Image.open(imageName).convert("RGB")
    except IOError:
        sys.exit("Failed to open image: " + imageName);
    width, height = image.size
    area = width * height
    pixelAmount = area // procNum
    extraPixels = area % procNum
    algorithmToDo = 2
    newImage = Image.new('RGB', image.size, (0,255,255))
    modifiedImage = newImage.load()
    
    pool = mp.Pool(procNum)
    for i in range(procNum):
        finalPixelAmount = pixelAmount
        #if(i == procNum -1):
        #    finalPixelAmount += extraPixels
        print "~~~~~~~~Worker #" + str(i) + " is being assigned~~~~~~~"
        pool.apply_async(workerProc, args = (i, imageName, algorithmToDo, finalPixelAmount, procNum ), callback = log_result)

    pool.close()
    pool.join()
    
    print "Done in %.4f seconds" % time.clock()
    newImage.save("out.jpg")