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
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

def imgResize(threadID, imageName, algoToRun, workload):
    print "~~~~~~~~~Worker #" + str(threadID) + " is starting~~~~~~~~~"
    image = Image.open(imageName).convert("RGB")
    if algoToRun == 0:
        newData = colourToGrey(image, workload, threadID)
    elif algoToRun == 1:
        print "n is a perfect square\n"
    elif algoToRun == 2:
        print "n is an even number\n"
    elif algoToRun == 3:
        print "n is a prime number\n"
    
    returnValue = {'threadID' : threadID, 'newData' : newData, 'pixelAmount' : workload}
    print "returned",threadID,workload
    return returnValue


def log_result(returnedValue):
    global modifiedImage
    threadID = returnedValue['threadID']
    returnedData = returnedValue['newData']
    pixelNum = returnedValue['pixelAmount']
    print "~~~~~~~~Worker #" + str(threadID) + " is done~~~~~~~"
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        modifiedImage[offX,offY] = returnedData[offX][offY]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("Not enough arguments provided")
    try:
        procNum = int(sys.argv[2])
        print procNum
    except ValueError:
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not a valid number")

    if not (99 > procNum > 1):
        sys.exit("Argument 2: '" + sys.argv[2] + "' (number of processors) is not between a valid range of 1 and 99")    
    time.clock
    
    imageName = assetDir + sys.argv[1]
    
    image = Image.open(imageName).convert("RGB")
    width, height = image.size
    area = width * height
    pixelAmount = area // procNum
    extraPixels = area % procNum
    algorithmToDo = 0
    newImage = Image.new('RGB', image.size, (0,255,255))
    modifiedImage = newImage.load()
    
    pool = mp.Pool(procNum)
    for i in range(procNum):
        finalPixelAmount = pixelAmount
        if(i == procNum -1):
            finalPixelAmount += extraPixels
        print "~~~~~~~~Worker #" + str(i) + " is being assigned~~~~~~~"
        pool.apply_async(imgResize, args = (i, imageName, algorithmToDo, finalPixelAmount ), callback = log_result)

    pool.close()
    pool.join()
    
    #worker = multiprocessing.Process(target=imgResize, args=(imageName,)) # use default name
    #worker.start()
    #print pool.map(imgResize, im1)
    #worker.join()
    print "Done in %.2f seconds" % time.clock()
    newImage.save("out.jpg")

def colourToGrey(image, pixelNum, threadID):
    width, height = image.size
    data = image.load()
    newData = [[0 for x in xrange(height)] for x in xrange(width)]
    offsetX = (pixelNum * threadID) % width
    offsetY = (pixelNum * threadID) // width
   
    print offsetX, offsetY
    
    for i in range(0, pixelNum):
        offX = (offsetX + i) % width
        offY = offsetY + ((offsetX + i) // width)
        # grey conversion from http://stackoverflow.com/a/15686412
        R_linear = sRGB_to_linear(data[offX,offY][0]/255.0)
        G_linear = sRGB_to_linear(data[offX,offY][1]/255.0)
        B_linear = sRGB_to_linear(data[offX,offY][2]/255.0)
        #print i,"\\",pixelNum," ", "rawData",offX,offY,"=",0.299 * R_linear + 0.587 * G_linear + 0.114 * B_linear
        #newData[offY][offX] = 0.299 * R_linear + 0.587 * G_linear + 0.114 * B_linear
        newData[offX][offY] = (125,125,125)
    print "fin"
    return newData


# Taken from http://stackoverflow.com/a/15686412
def sRGB_to_linear(x):
    if (x < 0.04045):
        return x/12.92
    return pow(((x+0.055)/1.055),2.4)