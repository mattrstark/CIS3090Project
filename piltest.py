from PIL import Image
import time
import sys
import multiprocessing, logging
logger = multiprocessing.log_to_stderr()
logger.setLevel(multiprocessing.SUBDEBUG)


global assetDir
global saveDir
global ext
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

def imgResize(imageName):
    im1 = Image.open(imageName).convert("RGB")
    div = 2
    width = im1.size[0] / div
    height = im1.size[1] / div

    im2 = im1.resize((width, height), Image.NEAREST) # use nearest neighbour
    im3 = im1.resize((width, height), Image.BILINEAR) # linear interpolation in a 2x2 environment
    im4 = im1.resize((width, height), Image.BICUBIC) # cubic spline interpolation in a 4x4 environment
    im5 = im1.resize((width, height), Image.ANTIALIAS) # best down-sizing filter
    
    im2.save(saveDir + "NEAREST" + ext)
    im3.save(saveDir + "BILINEAR" + ext)
    im4.save(saveDir + "BICUBIC" + ext)
    im5.save(saveDir + "ANTIALIAS" + ext)

    print "Worker is done"


if __name__ == '__main__':
    #pool = Pool(processes=2)
    if len(sys.argv) < 2:
        sys.exit("Not enough arguments provided")
    time.clock
    imageName = assetDir + sys.argv[1]
    
    worker = multiprocessing.Process(target=imgResize, args=(imageName,)) # use default name
    worker.start()
    #print pool.map(imgResize, im1)
    worker.join()
    print "Done in %.2f seconds" % time.clock()


