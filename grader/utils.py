import cv2
import numpy as np
import sys

class Utils:
    def find_questions(cnts, image):
        questions = []
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)
            if (w >= 15 and h >= 15) and (w <= 50 and h <= 50) and ar >= 0.7 and ar <= 1.3:
                box = [(x//5)*5, y]
                questions.append([c, box])

        return questions

    def find_ques_cnts(questions, width):
        questions = sorted(questions, key=lambda q: q[1][1])
        questionCnts = []

        for i in np.arange(0, len(questions), width):
            q = list(questions[i: i+width])
            q = sorted(q, key=lambda k: k[1][0])
            for o in q:
                questionCnts.append(o[0])

        return questionCnts

    def convert_ques_no(q, rows_cnt, cols_cnt, hori_to_vert=True):
        if hori_to_vert:
            row = q // cols_cnt
            col = q % cols_cnt
            return col * rows_cnt + row
        col = q // rows_cnt
        row = q % rows_cnt
        
        return row * cols_cnt + col
