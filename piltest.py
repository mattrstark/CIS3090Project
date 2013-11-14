from PIL import Image
import time
import sys
import multiprocessing as mp
import logging
logger = mp.log_to_stderr()
logger.setLevel(mp.SUBDEBUG)


global assetDir
global saveDir
global ext
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

def imgResize(threadID, imageName):
    print "~~~~~~~~~Worker #" + str(threadID) + " is starting~~~~~~~~~"
    im1 = Image.open(imageName).convert("RGB")
    div = 2
    width = im1.size[0] / div
    height = im1.size[1] / div

    im2 = im1.resize((width, height), Image.NEAREST) # use nearest neighbour
    im3 = im1.resize((width, height), Image.BILINEAR) # linear interpolation in a 2x2 environment
    im4 = im1.resize((width, height), Image.BICUBIC) # cubic spline interpolation in a 4x4 environment
    im5 = im1.resize((width, height), Image.ANTIALIAS) # best down-sizing filter
    
    im2.save(saveDir + "NEAREST" + str(threadID) + ext)
    im3.save(saveDir + "BILINEAR" + str(threadID) + ext)
    im4.save(saveDir + "BICUBIC" + str(threadID) + ext)
    im5.save(saveDir + "ANTIALIAS" + str(threadID) + ext)

    return threadID


def log_result(threadID):
    print "~~~~~~~~Worker #" + str(threadID) + " is done~~~~~~~"

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

    pool = mp.Pool(procNum)
    for i in range(procNum):
        print "~~~~~~~~Worker #" + str(i) + " is being assigned~~~~~~~"
        pool.apply_async(imgResize, args = (i, imageName, ), callback = log_result)

    pool.close()
    pool.join()
    
    #worker = multiprocessing.Process(target=imgResize, args=(imageName,)) # use default name
    #worker.start()
    #print pool.map(imgResize, im1)
    #worker.join()
    print "Done in %.2f seconds" % time.clock()


