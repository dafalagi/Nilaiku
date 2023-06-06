import cv2

class Utils:
    def rectContour(contours):
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

    def getCornerPoints(cont):
        peri = cv2.arcLength(cont, True)
        approx = cv2.approxPolyDP(cont, 0.02*peri, True)
        return approx