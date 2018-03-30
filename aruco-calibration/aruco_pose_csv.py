import pdb
from time import time, sleep
import numpy as np
import cv2
import glob

import cv2.aruco as aruco

cap = cv2.VideoCapture(0)

def read_node_matrix( reader, name ):
    node = reader.getNode( name )
    return node.mat()

# LOAD DICTIONARY
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

# length from the generated markers
# TODO maker a configuration file
aruco_marker_length_meters = 0.06858

# read the cameraParameters.xml file generated by
# opencv_interactive-calibration
camera_reader = cv2.FileStorage()
#camera_reader.open("cameraParameters.xml",cv2.FileStorage_READ)
camera_reader.open("../profiles/cameraParameters-PK-MHC-Heathers-Overhead-C920.xml",cv2.FileStorage_READ)

# camera configurations
camera_matrix = read_node_matrix( camera_reader, "cameraMatrix" )
dist_coeffs   = read_node_matrix( camera_reader, "dist_coeffs" )

while(True):
    sleep( 0.1 )
    # Read frame from Camera
    # convert frame to grayscale
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    # identify markers and
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict)
    frame = aruco.drawDetectedMarkers(frame, corners, ids )

    if( ids is not None ):
        rvecs,tvecs, objpoints = aruco.estimatePoseSingleMarkers( corners, aruco_marker_length_meters,
        #rvecs,tvecs = aruco.estimatePoseSingleMarkers( corners, aruco_marker_length_meters,
                camera_matrix, dist_coeffs )
        for i in range(len(rvecs)):
            tag_id = ids[i][0]
            frame = aruco.drawAxis( frame, camera_matrix, dist_coeffs, rvecs[i], tvecs[i], aruco_marker_length_meters )
            a = rvecs[i][0][0]
            b = rvecs[i][0][1]
            c = rvecs[i][0][2]
            x = tvecs[i][0][0]
            y = tvecs[i][0][1]
            z = tvecs[i][0][2]
            print("{},{},{},{},{},{},{},{}".format(time(),tag_id,a,b,c,x,y,z))

    # imshow and waitKey are required for the window
    # to open on a mac.
    cv2.imshow('frame', frame)

    if( cv2.waitKey(1) & 0xFF == ord('q') ):
        break

cap.release()
cv2.destroyAllWindows()

