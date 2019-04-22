from __future__ import print_function
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
#from mysql.connector import errorcode
from datetime import date, datetime, timedelta
import numpy as np
import argparse
import imutils
import cv2
import mysql.connector
import os

patientName = 'Shannon'
path1 = 'Desktop/testResults/' + patientName + '/results.txt'
path2 = 'Desktop/testResults/' + patientName + '/components'
testFailed = False
indurationSize = 3.2
results = 'TBneg'
contoursDetected = 2


def writeData(path1, path2, testFailed, indurationSize, results, contoursDetected, patientName):
    # writes values in parameters to a text file (results.txt)

    # open results.txt in writing mode (!! ASSUMES results.txt IS IN WORKING DIRECTORY !!)
    r = open('results.txt','w')
    # write parameter values into results.txt
    r.write(path1 + '\n')
    r.write(path2 + '\n')
    r.write(str(testFailed) + '\n')
    r.write(str(indurationSize) + '\n')
    r.write(results + '\n')
    r.write(str(contoursDetected) + '\n')
    # close results.txt
    r.close()

    #r = open('results.txt', 'r')
    #print(r.read())
    #r.close()

def insertData(path1, path2, testFailed, indurationSize, results, contoursDetected, patientName):
    # inserts values in parameters into the DB

    # convert testFailed from boolean to int
    if testFailed == False:
        testFailed = 0
    else:
        testFailed = 1


    # connect to DB
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Monkeydude",
        database="UCSF_app"
    )

    mycursor = mydb.cursor()

    # run the INSERT command with the given parameters
    sql = "INSERT INTO Results (resultsID, path1, path2, testFailed, indurationSize, results, contoursDetected, patientName) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    val = ("32", path1, path2, str(testFailed), str(indurationSize), results, str(contoursDetected), patientName)
    mycursor.execute(sql, val)

    # commit changes
    mydb.commit()

    print(mycursor.rowcount, "record inserted.")


writeData(path1, path2, testFailed, indurationSize, results, contoursDetected, patientName)
insertData(path1, path2, testFailed, indurationSize, results, contoursDetected, patientName)


# 2 (x,y tuple) return 1 (x,y tuple)
def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-w", "--width", type=float, required=True,
	help="width of the left-most object in the image (in inches)")
ap.add_argument("-u", "--user", required=True,
	help="Username of ")
args = vars(ap.parse_args())

# load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 150)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

# find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
(cnts, _) = contours.sort_contours(cnts)
pixelsPerMetric = None
countourCount = 0
print("Program starting")
# loop over the contours individually
for c in cnts:


	# if the contour is not sufficiently large, ignore it
	if cv2.contourArea(c) < 10:
		continue
	countourCount=countourCount+1
	print(countourCount)
	if countourCount == 1:
	 	print('This is the scaling reference, should be: '+ str(args["width"]))
	# compute the rotated bounding box of the contour
	orig = image.copy()
	box = cv2.minAreaRect(c)
	box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
	box = np.array(box, dtype="int")

	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)
	cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

	# loop over the original points and draw them
	for (x, y) in box:
		cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

	# unpack the ordered bounding box, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates
	(tl, tr, br, bl) = box
	print(box)
	(tltrX, tltrY) = midpoint(tl, tr)
	(blbrX, blbrY) = midpoint(bl, br)

	# compute the midpoint between the top-left and bottom-left points,
	# followed by the midpoint between the top-righ and bottom-right
	(tlblX, tlblY) = midpoint(tl, bl)
	(trbrX, trbrY) = midpoint(tr, br)

	# draw the midpoints on the image
	cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
	cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

	# draw lines between the midpoints
	cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
		(255, 0, 255), 2)
	cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
		(255, 0, 255), 2)

	# compute the Euclidean distance between the midpoints
	dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
	dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

	# if the pixels per metric has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, inches)
	if pixelsPerMetric is None:
		pixelsPerMetric = dB / args["width"]

	# compute the size of the object
	dimA = dA / pixelsPerMetric
	dimB = dB / pixelsPerMetric

	# draw the object sizes on the image
	cv2.putText(orig, "{:.1f}in".format(dimA),
		(int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)
	cv2.putText(orig, "{:.1f}in".format(dimB),
		(int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (255, 255, 255), 2)

	# show the output image
	cv2.imshow("Image", orig)


#	cv2.imwrite(os.path.join('/Users/Ooga/Desktop/Skin-Analyzer/pythonServer/components/'+str(args["user"]) , 'component'+str(countourCount)+'.jpg'), orig)
	cv2.waitKey(0)

# Make sure data is committed to the database
#	cnx.commit()

