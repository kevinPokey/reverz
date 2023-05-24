import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import median_filter
from reportlab.pdfgen import canvas


def isImageFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS


def makeImageTransparent():
    sessionUser = session["user"].get("name").replace(" ", "").lower()
    img = Image.open(f"{sessionUser}/signature.png")
    rgba = img.convert("RGBA")

    npImg = np.array(rgba)
    grayImage = ImageOps.grayscale(img)
    grayImage = median_filter(grayImage, size=4)
    grayNpImg = np.array(grayImage)
    swappedGrayNpImg = np.swapaxes(grayNpImg, 0, 1)

    imageSearch = np.array(np.where(grayNpImg < 240))
    firstLeft = imageSearch[0][0]
    lastRight = imageSearch[0][imageSearch.shape[1] - 1]
    imageSearch = np.array(np.where(swappedGrayNpImg < 240))
    firstRow = imageSearch[0][0]
    lastRow = imageSearch[0][imageSearch.shape[1] - 1]

    grayNpImg = grayNpImg[firstLeft:lastRight, firstRow:lastRow]
    npImg = npImg[firstLeft:lastRight, firstRow:lastRow]
    whitePixels = np.array(np.where(grayNpImg > 240))
    npImg[whitePixels[0, :], whitePixels[1, :], 3] = 0


    validMistakeInPixels = 10
    maxCounter = 0
    bestRow = 0

    i = validMistakeInPixels
    
    for i in range(grayNpImg.shape[0] - validMistakeInPixels * 2):
        j = -validMistakeInPixels
        counter = 0
        for j in range(validMistakeInPixels * 2 + 1):
            rowIndex = i + j
            currentRow = grayNpImg[rowIndex]
            blackPixels = np.asarray(np.where(currentRow != 255))
            for k in blackPixels[0]:
                try:
                    if grayNpImg[rowIndex + 1][k] == 255 and grayNpImg[rowIndex + 1][k-1] == 255 and grayNpImg[rowIndex + 1][k+1] == 255:
                        counter = counter + 1
                except:
                    pass
            if counter > maxCounter:
                maxCounter = counter
                bestRow = rowIndex


    pilImg = Image.fromarray(npImg)
    pilImg.save(f"{sessionUser}/signature.png", "PNG")
    return abs(((bestRow * 100) / grayNpImg.shape[0]) - 100)