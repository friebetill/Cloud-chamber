import numpy as np
import os
import math
import cv2
from random import randint
import pandas

##################################################
#                     Class                      #
##################################################
class Line:
    def __init__(self, x1, y1, x2, y2, filename):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.filename = filename
        self.length = length(x1, y1, x2, y2)
        self.angle = angleBetween(x1, y1, x2, y2)


    def getPoints(self):
        return(self.x1, self.y1, self.x2, self.y2)

def createLinesWithClass(lines, filename):
    '''Transforms an array of full points into an array with the lines'''
    tmpLines = []
    for line in lines:
        (x1, y1, x2, y2) = line
        tmpLines.append(Line(x1, y1, x2, y2, filename))
    return tmpLines

def linesToDataFrame(lines):
    tmp = {'filename':[], 'length':[] ,'angle':[] ,'p1_x':[] ,'p1_y':[] ,'p2_x':[] ,'p2_y':[]}
    for line in lines:
        tmp['filename'].append(line.filename)
        tmp['length'].append(line.length)
        tmp['angle'].append(line.angle)
        tmp['p1_x'].append(line.x1)
        tmp['p1_y'].append(line.y1)
        tmp['p2_x'].append(line.x2)
        tmp['p2_y'].append(line.y2)

    return pandas.DataFrame(tmp)

##################################################
#                    Function                    #
##################################################
def filterLines(lines):
    angle_tolerance = 10

    linesByAngle = sortByAngle(lines, angle_tolerance)

    for linesSameAngle in linesByAngle:
        while connectTwoLinesIfPossible(linesSameAngle, angle_tolerance):
            pass

    # Flattens the list https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    return [item for sublist in linesByAngle for item in sublist]

##################################################
#                 Helper-Function                #
##################################################
def isAlmostSameAngle(angle1, angle2, tolerance):
    '''Compares whether the angles are similar, with a tolerance to each other'''
    sameAngleBut180Rotated = False
    if angle1 > angle2:
        sameAngleBut180Rotated = abs(((angle2 + 180) - angle1)) <= tolerance
    else:
        sameAngleBut180Rotated = abs(((angle1 + 180) - angle2)) <= tolerance
    return abs(angle1 - angle2) <= tolerance or \
           abs(angle1 - 180) <= tolerance or \
           abs(angle1 + 180) <= tolerance or \
           sameAngleBut180Rotated

def listImages(path):
    '''Lists all images in the specified folder'''
    images = []
    acceptedImages = ['png', 'jpg', 'JPG']

    for entry in os.scandir(path):
        if entry.name[-3:] in acceptedImages and entry.is_file():
            images.append(entry.name)

    if len(images) == 0:
        print('No images in the folder ' + path)

    images = sorted(images)
    return images

def angleBetween(x1, y1, x2, y2):
    '''Returns angle from -180 to 180 relativ to the horizontal'''
    return math.degrees(np.arctan2(y2-y1, x2-x1))

def length(x1, y1, x2, y2):
    '''Calculates the length of the line'''
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

def sortByAngle(lines, angle_tolerance):
    '''Sorts all lines into different arrays depending on their angle'''
    linesByAngle = []
    angles = []
    for i_line, line in enumerate(lines):
        for i_angle, angle in enumerate(angles):
            if isAlmostSameAngle(angle, line.angle, angle_tolerance):
                linesByAngle[i_angle].append(line)
                angles[i_angle] = (angle + line.angle) / 2
                break
        else:
            angles.append(line.angle)
            linesByAngle.append([line])

    return linesByAngle

def calculateShortestLine(x1,y1,x2,y2,x3,y3,x4,y4,filename):
   '''Calculates the shortest line from all points'''
   shortest = np.argmin([length(x1,y1,x3,y3), length(x1,y1,x4,y4), length(x2,y2,x3,y3), length(x2,y2,x4,y4)])
   if shortest == 0:
       return Line(x1,y1,x3,y3, filename)
   elif shortest == 1:
       return Line(x1,y1,x4,y4, filename)
   elif shortest == 2:
       return Line(x2,y2,x3,y3, filename)
   else:
       return Line(x2,y2,x4,y4, filename)

def calculateLongestLine(x1,y1,x2,y2,x3,y3,x4,y4,filename):
   '''Calculates the longest line from all points'''
   shortest = np.argmax([length(x1,y1,x2,y2), length(x1,y1,x3,y3), \
                         length(x1,y1,x4,y4), length(x2,y2,x3,y3), \
                         length(x2,y2,x4,y4), length(x3,y3,x4,y4)])
   if shortest == 0:
       return Line(x1,y1,x2,y2, filename)
   elif shortest == 1:
       return Line(x1,y1,x3,y3, filename)
   elif shortest == 2:
       return Line(x1,y1,x4,y4, filename)
   elif shortest == 3:
       return Line(x2,y2,x3,y3, filename)
   elif shortest == 4:
       return Line(x2,y2,x4,y4, filename)
   else:
       return Line(x3,y3,x4,y4, filename)

def connectTwoLinesIfPossible(lines, angle_tolerance):
    '''Tries to connect two lines with equal angles, depends on whether the lines are close to each other.'''
    for i_line_1 in range(len(lines)):
        (x1,y1,x2,y2) = lines[i_line_1].getPoints()

        for i_line_2 in range(i_line_1+1, len(lines)):
            (x3,y3,x4,y4) = lines[i_line_2].getPoints()
            shortestLine = calculateShortestLine(x1,y1,x2,y2,x3,y3,x4,y4,lines[i_line_1].filename)
            longestLine = calculateLongestLine(x1,y1,x2,y2,x3,y3,x4,y4,lines[i_line_1].filename)

            if shortestLine.length > (lines[i_line_1].length + lines[i_line_2].length) / 4:
                continue

            if isAlmostSameAngle(shortestLine.angle, lines[i_line_1].angle, angle_tolerance) or \
               shortestLine.length < (lines[i_line_1].length + lines[i_line_2].length) / 4 and \
               isAlmostSameAngle(longestLine.angle, lines[i_line_1].angle, angle_tolerance):

                del(lines[i_line_2])
                del(lines[i_line_1])
                lines.append(longestLine)
                return True
    return False

def colorImageWithLines(lines, image):
    '''Draws lines in the given image'''
    for line in lines:
        cv2.line(image, (line.x1, line.y1), (line.x2, line.y2), color=(randint(100, 255), randint(100, 255), randint(100, 255)), thickness=3)
    return image

##################################################
#             Unused Helper-Function             #
##################################################
def getPointsOnLine(line):
    '''Creates points on lines with even spacing'''
    (x1,y1,x2,y2) = line
    vec = (x1-x2, y1-y2)
    length_line = np.sqrt((x1-x2)**2 + (y1-y2)**2)
    vec = np.divide(vec, length_line*10)
    dots = []
    for i in range(1, int(length_line*10)):
        dots.append((x1+vec[0]*i, y1+vec[1]*i))
    return dots

# Does not deal well with colinearity, source https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def intersect(line1,line2):
    '''Determines whether two lines intersect'''
    (x1, y1, x2, y2) = line1
    (x3, y3, x4, y4) = line2
    A = [x1, y1]
    B = [x2, y2]
    C = [x3, y3]
    D = [x4, y4]
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def ccw(A,B,C):
    '''Help function for intersect'''
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
