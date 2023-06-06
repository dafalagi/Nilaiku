from imutils.perspective import four_point_transform
from decouple import config
import tinify, cv2, os

class Utils:
    def isTiny(self, file):
        tinify.key = config('TINIFY_KEY')

        img = cv2.imread('media/'+file.name)
        dimensions = img.shape
        height = dimensions[0]
        width = dimensions[1]

        if width > 2000 or height > 2000:
            source = tinify.from_file('media/'+file.name)
            source.to_file('media/'+file.name)

        return True

    def preprocessing(self, file):
        img = cv2.imread('media/'+file.name)

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
        imgCanny = cv2.Canny(imgBlur, 20, 50)

        return imgCanny

    def warping(self, file):
        img = cv2.imread('media/'+file.name)
        preprocessed = self.preprocessing(file)

        contours, hierarchy = cv2.findContours(preprocessed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rectCont = self.rectContour(contours)
        biggestContour = self.getCornerPoints(rectCont[0])

        if biggestContour.size != 0:
            imgOutput = four_point_transform(img, biggestContour.reshape(4, 2))

            basename = os.path.basename(file.name)
            cv2.imwrite('media/images/warped'+basename, imgOutput)
            warped = 'images/warped'+basename

            return warped
            
    def rectContour(self, contours):
        rectCon = []
        maxArea = 0

        for i in contours:
            area = cv2.contourArea(i)
            if area > 50:
                peri = cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, 0.02*peri, True)
                if len(approx) == 4:
                    rectCon.append(i)

        rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)

        return rectCon

    def getCornerPoints(self, cont):
        peri = cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, 0.02*peri, True)

        return approx