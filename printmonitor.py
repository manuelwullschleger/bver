# TODO: RENAME FILE
import numpy as np
import matplotlib.pyplot as plt
import cv2

class PrintState:
    STARTING = 0
    LAYER_PRINTING = 1
    LAYER_FINISHED = 2
    PRINT_FINISHED = 3

class PrintMonitoring:
    videoSource = 0
    usePreRecordedVideo = False
    headRoi = None
    printerRoi = None
    frameRateInFPS = 25
    def __init__(self, videoSource, cameraConfig, usePreRecordedVideo = False, frameRateInFPS = 25):
        headRoi, printerRoi = cameraConfig
        self.headRoi = headRoi
        self.printerRoi = printerRoi
        self.videoSource = videoSource
        self.usePreRecordedVideo = usePreRecordedVideo
        self.frameRateInFPS = frameRateInFPS
    
    def getImage(self, drawRegions = False, cutToRoi = False):
        cam = cv2.VideoCapture(self.videoSource)
        ret, frame = cam.read()
        if(drawRegions):
            x,y,w,h = self.headRoi
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0))

            xp,yp,wp,hp = self.printerRoi
            cv2.rectangle(frame, (xp,yp), (xp+wp, yp+hp), (0,255,0))

        if(cutToRoi):
            x, y, w, h = self.printerRoi
            frame = frame[y:y+h, x:x+w]
            
        cam.release()
        return frame
    
    def setCameraConfig(self, cameraConfig):
        headRoi, printerRoi = cameraConfig
        self.headRoi = headRoi
        self.printerRoi = printerRoi

    def delayedStateChange(self, oldState, newState, stateCounter, stateChangeDelayInMs):
        stateCounter += 1000/self.frameRateInFPS
        if(newState == oldState):
            stateCounter = 0
            return (oldState, stateCounter)
        elif(stateCounter >= stateChangeDelayInMs):
            stateCounter = 0
            return (newState, stateCounter)
        else:
            return (oldState, stateCounter)

    def trackPrint(self, layerDoneCallback, config):
        cap = cv2.VideoCapture(self.videoSource)
        frameCounter = 0
        ret, frame = cap.read()
        printState = PrintState.STARTING
        headInRoi = False
        notified = False
        stateCounter = 0
        layerNumber = 0
        stateChangeDelayInMs = 100
        trackFrame = np.zeros((frame.shape[0],frame.shape[1]), np.uint8)
        while(cap.isOpened()):
            ret, frame = cap.read()
            hsv =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower = (35, 44, 85)
            upper = (75, 255, 255)

            binary = cv2.inRange(hsv, lower, upper)
            cv2.erode(binary, np.ones((5,5), np.uint8), dst=binary, iterations=3)
            cv2.dilate(binary, np.ones((5,5), np.uint8), dst=binary, iterations=2)

            trackFrame = cv2.bitwise_and(binary, trackFrame)
            if(frameCounter % 3 == 0):
                x,y,w,h = cv2.boundingRect(trackFrame)
                xr, yr, wr, hr = self.headRoi
                headInRoi = ((x >= xr and x <= (xr + wr)) and (y >= yr and y <= (yr + hr)))
                cv2.imshow('trackFrame',trackFrame)
                trackFrame = binary
            
            cv2.rectangle(frame, (x,y),(x+w, y+h), (255,0,0) )
            cv2.rectangle(frame, (xr,yr),(xr+wr, yr+hr), (0,255,0) )
            cv2.imshow('frame',frame)

            if(printState == PrintState.STARTING):
                if((not headInRoi)):  
                   newState = PrintState.LAYER_PRINTING
                else:
                    newState = printState
            elif(printState == PrintState.LAYER_PRINTING):
                notified = False
                if(headInRoi):
                    newState = PrintState.LAYER_FINISHED
                else:
                    newState = printState
            elif(printState == PrintState.LAYER_FINISHED):
                if(not notified):
                    layerNumber += 1
                    #crop frame to printerroi
                    x, y, w, h = self.printerRoi
                    croppedFrame = frame[y:y+h, x:x+w]
                    layerDoneCallback(layerNumber, croppedFrame, config)
                    notified = True
                if(not headInRoi):
                      newState = PrintState.LAYER_PRINTING
                else:
                    newState = printState
            elif(printState == PrintState.PRINT_FINISHED):
                print("Print finished")
            
            printState, stateCounter = self.delayedStateChange(printState, newState, stateCounter, stateChangeDelayInMs)
            frameCounter += 1

            if cv2.waitKey(int(1000/self.frameRateInFPS)) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()