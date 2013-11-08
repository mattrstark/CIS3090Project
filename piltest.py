from PIL import Image

global assetDir
global saveDir
global ext
assetDir = "assets/"
saveDir = "results/"
ext = ".jpg"

def imgResize(im):

    div = 2
    width = im.size[0] / div
    height = im.size[1] / div

    im2 = im.resize((width, height), Image.NEAREST) # use nearest neighbour
    im3 = im.resize((width, height), Image.BILINEAR) # linear interpolation in a 2x2 environment
    im4 = im.resize((width, height), Image.BICUBIC) # cubic spline interpolation in a 4x4 environment
    im5 = im.resize((width, height), Image.ANTIALIAS) # best down-sizing filter
    
    im2.save(saveDir + "NEAREST" + ext)
    im3.save(saveDir + "BILINEAR" + ext)
    im4.save(saveDir + "BICUBIC" + ext)
    im5.save(saveDir + "ANTIALIAS" + ext)

imageFile = assetDir + "test.jpg"
im1 = Image.open(imageFile).convert("RGB")

imgResize(im1)



