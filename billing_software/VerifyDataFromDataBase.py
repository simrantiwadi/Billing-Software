# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import random
import math
import glob
import sqlite3
from matplotlib import pyplot as plt
from flask import Flask


#Paths for the images stored and to be stored
PATH_IMAGES = 'E:/Py/Obj Detect/New/'
files   = glob.glob(PATH_IMAGES+"Pic.png")
files1   = glob.glob(PATH_IMAGES+"Pic1.png")

#Connect to the database
conn = sqlite3.connect('ADDLOCALDATABASE.db') 
c = conn.cursor()
#cursor = conn.cursor()
#rows = c.fetchall()


def create_table(): 
	c.execute('CREATE TABLE IF NOT EXISTS CheckData (SR_Number REAL, ID REAL, Name TEXT, Price REAL, Quantity REAL, Length REAL, Width REAL, Image_Original BLOB, Image_Processed BLOB)')

 
def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
 
def Image_Capture():
        #Capture the image
        img = cv2.VideoCapture(0)
        return_value, image = img.read()
        cv2.imwrite('Pic'+'.png', image)

def Image_Process():
        # load the image, convert it to grayscale, and blur it slightly
        image = cv2.imread("E:/Py/Obj Detect/New/Pic.png")
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(img, (5, 5), 0)
        #gray = cv2.blur(img,(7,7))
        gray = cv2.addWeighted(gray,1.5,img,-0.5,0)
         
        # perform edge detection, then perform a dilation + erosion to close gaps in between object edges
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
         
        # find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
         
        # sort the contours from left-to-right and initialize the 'pixels per metric' calibration variable
        (cnts, _) = contours.sort_contours(cnts)
        #pixelsPerMetric = None
        
        # loop over the contours individually
        for c in cnts:

                # compute the rotated bounding box of the contour
                orig = image.copy()
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")

                # order the points in the contour such that they appear in top-left, top-right, bottom-right, and bottom-left order, then draw the outline of the rotated bounding box
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                # co-ordinates of the box in clockwise direction
                (t1, tr, br, b1) = box

                (t1trX, t1trY) = midpoint(t1, tr)  # Co-ordinates of midpoint between top left and top right
                (b1brX, b1brY) = midpoint(b1, br)  # Co-ordinates of midpoint between bottom left and bottom right 
                (t1b1X, t1b1Y) = midpoint(t1, b1)  # Co-ordinates of mid-point between top left and bottom left
                (trbrX, trbrY) = midpoint(tr, br)  # Co-ordinates of mid-point between top right and bottom right
               
                '''
                # compute the Euclidean distance between the midpoints
                dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
                dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
                '''

                # Distance between midpoints
                dA = math.sqrt(pow((trbrX-t1b1X),2) + pow((trbrY-t1b1Y),2))
                dB = math.sqrt(pow((t1trX-b1brX),2) + pow((t1trY-b1brY),2))

                pixelsPerMetric = 25
                dimA = dA / pixelsPerMetric
                dimB = dB / pixelsPerMetric

                length = math.ceil(dimA)
                width = math.ceil(dimB)

                # draw the object sizes on the image
                #cv2.putText(orig, "{:.2f}cm".format(dimA), (int(t1trX - 15), int(t1trY - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
                #cv2.putText(orig, "{:.2f}cm".format(dimB), (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

                # show the output image
                cv2.imwrite('Pic1'+'.png', orig)
                cv2.imshow("Image", orig)
                Image_Detect(length,width)
                #cv2.imshow("Image", orig)
                cv2.waitKey(0)
                break

def Image_Detect(length,width):
        cursor = conn.cursor()
        #length = float(input("Length : "))
        #width = float(input("Width : "))

        cursor.execute("SELECT ID, Name, Price, Quantity FROM CheckData WHERE (Length = %d AND Width = %d)"%(length,width))

        rows = cursor.fetchall()

        for row in rows:
            print(row)

           
#create_table()
Image_Capture()
Image_Process()

c.close()
#cursor.close()
conn.close() 