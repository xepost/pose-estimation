import pdb
import time
import numpy as np
import cv2
import glob

import cv2.aruco as aruco

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

def read_node_matrix( reader, name ):
    node = reader.getNode( name )
    return node.mat()

def draw_board_axis( board, board_corners, board_ids, frame, camera_matrix, dist_coeffs, axis_length ):
    corners = np.asarray(board_corners)
    ids     = np.asarray(board_ids)
    retval,rvec,tvec = aruco.estimatePoseBoard(corners, ids, board, camera_matrix, dist_coeffs)
    frame   = aruco.drawAxis( frame, camera_matrix, dist_coeffs, rvec, tvec, axis_length_inches)
    axis_origin = np.asarray( [[0,0,0]],dtype=np.float )
    imgpts, jac = cv2.projectPoints( axis_origin, rvec, tvec, camera_matrix, dist_coeffs )
    text_base = (int(imgpts[0][0][0]),int(imgpts[0][0][1])-100)
    #print(text_base)
    board_range = np.linalg.norm(tvec)
    board_range_str = "Range: {:.2f} meters".format( board_range )
    cv2.putText(frame, board_range_str, text_base, font, 1, (255,255,255),2,cv2.LINE_AA)
    return board_range

# LOAD DICTIONARY
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)

# length from the generated markers 
# TODO maker a configuration file
axis_length_inches = 0.0508
hexagon_corners = [
np.array([[-0.023,0.048,0.044], [0.023,0.048,0.044],  [0.023,0.003,0.044],  [-0.023,0.003,0.044]] ,dtype=np.float32),
np.array([[0.027,0.048,0.042],  [0.050,0.048,0.002],  [0.050,0.003,0.002],  [0.027,0.003,0.042]]  ,dtype=np.float32),
np.array([[0.050,0.048,-0.002], [0.027,0.048,-0.042], [0.028,0.003,-0.042], [0.050,0.003,-0.002]] ,dtype=np.float32),
np.array([[0.023,0.048,-0.044], [-0.023,0.048,-0.044],[-0.023,0.003,-0.044],[0.023,0.003,-0.044]] ,dtype=np.float32),
np.array([[-0.027,0.048,-0.042],[-0.050,0.048,-0.002],[-0.050,0.003,-0.002],[-0.027,0.003,-0.042]],dtype=np.float32),
np.array([[-0.049,0.048,0.002], [-0.027,0.048,0.042], [-0.028,0.003,0.042], [-0.049,0.003,0.002]] ,dtype=np.float32)]

port_board_ids = np.array( [[21],[22],[23],[24],[25],[26]], dtype=np.int32)
port_board     = aruco.Board_create( hexagon_corners, 
                                     aruco.getPredefinedDictionary(aruco.DICT_6X6_250),
                                     port_board_ids )

star_board_ids = np.array( [[27],[28],[29],[30],[31],[32]], dtype=np.int32)
star_board         = aruco.Board_create( hexagon_corners, 
                                    aruco.getPredefinedDictionary(aruco.DICT_6X6_250),
                                    star_board_ids )

# read the cameraParameters.xml file generated by
# opencv_interactive-calibration
camera_reader = cv2.FileStorage()
camera_reader.open("cameraParameters.xml",cv2.FileStorage_READ)

# camera configurations
camera_matrix = read_node_matrix( camera_reader, "cameraMatrix" )
dist_coeffs   = read_node_matrix( camera_reader, "dist_coeffs" )

while(True):
    time.sleep( 0.1 )
    # Read frame from Camera
    # convert frame to grayscale
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # identify markers and 
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict)
    frame = aruco.drawDetectedMarkers(frame, corners, ids)

    detected_port_ids     = list()
    detected_port_corners = list()

    detected_starboard_ids     = list()
    detected_starboard_corners = list()

    #print("ids = ", ids)
    #print("corners = ", corners)

    if( ids is not None ):
        for i in range(len(ids)):
            detected_id = ids[i]
            detected_corner = corners[i]
            #print( detected_id, detected_corner )
            if( detected_id in port_board_ids ):
                detected_port_ids.append( detected_id )
                detected_port_corners.append( detected_corner )
            elif( detected_id in star_board_ids ):
                detected_starboard_ids.append(detected_id)
                detected_starboard_corners.append(detected_corner)

    port_range_m = -1
    starboard_range_m = -1
    if( detected_port_ids ):
        port_range_m = draw_board_axis( port_board, detected_port_corners, detected_port_ids,
                         frame, camera_matrix, dist_coeffs, axis_length_inches )
    if( detected_starboard_ids ): 
        starboard_range_m = draw_board_axis( star_board, detected_starboard_corners, detected_starboard_ids,
                         frame, camera_matrix, dist_coeffs, axis_length_inches )

    print( "range( port ) = {:.2f}, range( starboard ) = {:.2f}".format( port_range_m, starboard_range_m ) )
    # imshow and waitKey are required for the window
    # to open on a mac.
    cv2.imshow('frame', frame)

    if( cv2.waitKey(1) & 0xFF == ord('q') ):
        break

cap.release()
cv2.destroyAllWindows()
