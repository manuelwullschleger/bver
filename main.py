# -------------------------------------------------
# Title: Tool to monitor FDM-3D Printers using image processing
# Author: Manuel Wullschleger & Marc Röthlisberger
# Date: 12-06-2020
# Version: 1.0
# Availability: https://gitlab.fhnw.ch/manuel.wullschleger/bverproject
# -------------------------------------------------
from printmonitor import PrintMonitoring
from getlayerimages import createLayerImages
from imageprocessing import ImageProcessor
import cv2
import argparse
import configparser
import sys
import os
import uuid
tempFolder = None

def main(): 

    # parse command line arguments using argparse (https://docs.python.org/3/library/argparse.html)
    ap = argparse.ArgumentParser(description='Ultimaker 3d-Print monitoring tool by Marc Röthlisberger & Manuel Wullschleger')
    ap.add_argument("-g", dest="gcodePath", metavar="PathToGCodeFile", type=str, help='Path to the gcode file')
    ap.add_argument("-w", dest="webcam", metavar="webcamId", type=int, help='Define webcam to use for print monitoring')
    ap.add_argument("-v", dest="videoSource", metavar="PathToVideoFile", type=str, help='Run for pre-recorded video')
    ap.add_argument("-s", dest='startMonitoring', action='store_true', help='Starts print monitoring for gcode file using defined webcam or video source')
    ap.add_argument("-t", dest='showTest', action='store_true', help='Show test image to validate video source')
    ap.add_argument("-c", dest='configure', action='store_true', help='Configure ROIs')
    args = ap.parse_args()

    if(args.showTest):
        source = None
        #validate arguments
        if(args.videoSource is not None):
           source = args.videoSource
        elif(args.webcam is not None):
            source = args.webcam
        else:
            ap.error("A webcam or a videoSource is required to get an image. Provide a VideoSource using parameter -v or specify a Webcam using parameter -w")
       
        if(source is not None):
            cameraConfig = getCameraConfig()
            monitor = PrintMonitoring(source, cameraConfig)
            img = monitor.getImage(True, False)
            cv2.imshow("Test image", img)
            cv2.waitKey()
        
    elif(args.configure):
        #validate arguments
        if(args.videoSource is not None):
            selectCameraConfig(args.videoSource)
        elif(args.webcam is not None):
            selectCameraConfig(args.webcam)
        else:
            ap.error("A webcam or a videoSource is required to configure monitoring. Provide a VideoSource using parameter -v or specify a Webcam using parameter -w")
    
    elif(args.startMonitoring):
        #validate arguments
        if(args.gcodePath is None):
             ap.error("The path to a Gcode file is reqired to start monitoring. Provide a Gcode using parameter -g PATH")
        elif(args.videoSource is not None):
            startMonitoring(args.gcodePath, args.videoSource)
        elif(args.webcam is not None):
            startMonitoring(args.gcodePath, args.webcam)
        else:
            ap.error("A webcam or a videoSource is required to start monitoring. Provide a VideoSource using parameter -v or specify a Webcam using parameter -w")
    else:
        ap.print_help()

def getCameraConfig():
    #load configuration from settings.ini
    config = configparser.ConfigParser()
    config.read("config.ini")
    hx = config["headRoi"].getint("x")
    hy = config["headRoi"].getint("y")
    hw = config["headRoi"].getint("w")
    hh = config["headRoi"].getint("h")

    px = config["printerRoi"].getint("x")
    py = config["printerRoi"].getint("y")
    pw = config["printerRoi"].getint("w")
    ph = config["printerRoi"].getint("h")

    printerRoi = (px, py, pw, ph)
    headRoi = (hx, hy, hw, hh)
    return (headRoi, printerRoi)

def storeCameraConfig(cameraConfig):
    #save configuration to settings.ini
    headRoi, printerRoi = cameraConfig
    config = configparser.ConfigParser()

    hx, hy, hw, hh = headRoi
    config['headRoi'] = {}
    config["headRoi"]["x"] = str(hx)
    config["headRoi"]["y"] = str(hy)
    config["headRoi"]["w"] = str(hw)
    config["headRoi"]["h"] = str(hh)
    
    px, py, pw, ph = printerRoi
    config['printerRoi'] = {}
    config["printerRoi"]["x"] = str(px)
    config["printerRoi"]["y"] = str(py)
    config["printerRoi"]["w"] = str(pw)
    config["printerRoi"]["h"] = str(ph)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def getSollImage(sollPath, layerNumber):
    sollPath = os.path.join(sollPath, str(layerNumber) + ".png")
    im = cv2.imread(sollPath)
    return im

# gets called by printmonitor.py after each finished layer
def layerDone(layerNumber, istImage, config):
    istPath, sollPath, imageProcessor = config
    sollImage = getSollImage(sollPath, layerNumber)
    cv2.imwrite(os.path.join(istPath, str(layerNumber) + ".jpg"), istImage)
    # calculate match between ist & soll
    success, match = imageProcessor.getMatch(istImage, sollImage)
    
    if(success):
        print("Layer " + str(layerNumber) + " complete. Match: " + str(match))
    else:
        print("Layer " + str(layerNumber) + " complete. No match found")
        match = 0

    if(match < 0.55):
        stop = True
        print("Print error detected. Stopping print..")
        #stop print here, not implemented yet

def startMonitoring(gcodePath, videoSource):
    #create folder to store ist & soll-images
    tempFolder = uuid.uuid4().hex
    os.mkdir(tempFolder)

    sollPath = os.path.join(tempFolder, "soll")
    os.mkdir(sollPath)

    istPath = os.path.join(tempFolder, "ist")
    os.mkdir(istPath)

    print("Temp folder: " + tempFolder)
    print("Plotting layers (this might take a while)")
    #create soll-images and store to tempfolder
    createLayerImages(gcodePath, sollPath, True) 

    cameraConfig = getCameraConfig() #load camera configuration
    monitor = PrintMonitoring(videoSource, cameraConfig, True, 200) #set up print monitoring

    emptyPrinter = monitor.getImage(drawRegions=False, cutToRoi=True) #get empty printer image for mask creation
    imageProcessor = ImageProcessor(emptyPrinter) #set up image processor
    
    monitor.trackPrint(layerDone, (istPath, sollPath, imageProcessor)) #start monitoring

def selectCameraConfig(videoSource):
    cameraConfig = getCameraConfig()
    monitor = PrintMonitoring(videoSource, cameraConfig)
    img = monitor.getImage(True)
    headRoi, printerRoi = cameraConfig
    print("Select print head ROI")
    headRoi = cv2.selectROI("Select print head roi", img)
    if(all(headRoi)):
        cameraConfig = headRoi, printerRoi
        monitor.setCameraConfig(cameraConfig)
   
    img = monitor.getImage(True)
    print("Select printer ROI")
    printerRoi = cv2.selectROI("Select printer roi", img)
    if(all(printerRoi)):
        cameraConfig = headRoi, printerRoi
        monitor.setCameraConfig(cameraConfig)
    
    storeCameraConfig(cameraConfig)

    cv2.imshow("selection",monitor.getImage(True))
    cv2.waitKey(0)

if __name__ == '__main__':
    main()