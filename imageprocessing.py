# -------------------------------------------------
# Title: Calculates the quality of a printed layer
# Author: Manuel Wullschleger & Marc Röthlisberger
# Date: 12-06-2020
# Version: 1.0
# Availability: https://gitlab.fhnw.ch/manuel.wullschleger/bverproject
# -------------------------------------------------
import cv2
import numpy as np
import random 
import matplotlib.pyplot as plt
class ImageProcessor:
    DEBUG = 1 #set to True to show every step
    emptyPrinterImage = None
    def __init__(self, emptyPrinterImage):
        self.emptyPrinterImage = emptyPrinterImage
    
    def cropToBBox(self, im):
        x, y, w, h = cv2.boundingRect(im)
        imcroped = im[y:y+h, x:x+w]
        size =  (x, y, w, h)
        return (imcroped, size)

    def getBinary(self, imgEdges, imgRaw):
        x, y, w, h = cv2.boundingRect(imgEdges)
        imcroped = imgRaw[y:y+h, x:x+w]
        imbin = cv2.adaptiveThreshold(imcroped, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 199,40)
        img = np.zeros(imgRaw.shape, np.uint8)
        img[y:y+h, x:x+w] = imbin
        return img

    def getMask(self, emptyPrinterImage):
        im_empty = emptyPrinterImage
        mask = cv2.Canny(im_empty, 100, 200)
        # - dilate mask
        kernel = np.ones((90, 90),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations = 1)
        mask =  cv2.bitwise_not(mask)
        return mask

    def getMatch(self, imIst, imSoll):
        im_ist_raw = cv2.cvtColor(imIst, cv2.COLOR_BGR2GRAY)
        im_soll_raw = cv2.cvtColor(imSoll, cv2.COLOR_BGR2GRAY)
        mask = self.getMask(self.emptyPrinterImage)

        if self.DEBUG:
            cv2.imshow("ist", im_ist_raw)
            cv2.imshow("soll", im_soll_raw)
            cv2.imshow("mask", mask)
            cv2.waitKey(0)

        # druck freistellen: 
        # - edge dedector für druck
        print_contures = cv2.Canny(im_ist_raw, 100, 200)
        print_soll = cv2.Canny(im_soll_raw, 100, 200)

        if self.DEBUG:
            cv2.imshow("ist", print_contures)
            cv2.imshow("soll", print_soll)
            cv2.imshow("empty", mask)
            cv2.waitKey(0)

        # - apply mask to layer image, show result
        print_ist = cv2.bitwise_and(print_contures, mask)

        if self.DEBUG:
            cv2.imshow("ist", print_ist)
            cv2.imshow("soll", print_soll)
            cv2.imshow("empty", mask)
            cv2.waitKey(0)

        # vergleiche ist und soll
        #  - create template
        template, (x, y, w, h) = self.cropToBBox(print_soll)
        templateRaw = im_soll_raw[y:y+h, x:x+w]

        # - ermittle koordinaten höchster übereinstimmung von soll in ist bild (template matching)
        max_find = None
        top_left = 0
        bottom_right = 0
        matchingTemplate = None
        for scale in np.linspace(0.5, 1.5, 40):
            temp = np.copy(template)
            dsize = (int(temp.shape[1]*scale), int(temp.shape[0]*scale))
            resized_template = cv2.resize(temp, dsize, interpolation=cv2.INTER_LINEAR_EXACT)
            method = cv2.TM_CCOEFF
            res = cv2.matchTemplate(print_ist, resized_template, method)
            h, w = resized_template.shape
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if(max_val > 0 and (max_find is None or max_val > max_find)):
                max_find = max_val
                top_left = max_loc
                matchingSize = dsize
                bottom_right = (top_left[0] + w, top_left[1] + h)


        if(max_find is not None):
            #create comparison images

            matchingTemplate = cv2.resize(template, matchingSize, interpolation=cv2.INTER_LINEAR_EXACT)
            matchingTemplateRaw = cv2.resize(templateRaw, matchingSize, interpolation=cv2.INTER_LINEAR_EXACT)
            

            print_ist = self.getBinary(print_ist, im_ist_raw)
            matchingTemplate = self.getBinary(matchingTemplate, matchingTemplateRaw)

            #resize soll image to same dimensions as ist
            soll = np.zeros(print_ist.shape, dtype=np.uint8)
            x,y = top_left
            h, w = matchingTemplate.shape
            soll[y:y+h, x:x+w] = matchingTemplate

            #compare
            if(self.DEBUG):
                cv2.imshow("soll", soll)
                cv2.imshow("ist", print_ist)
            
            diff = cv2.bitwise_xor(print_ist,soll)
            
            if self.DEBUG:
                cv2.imshow("diff",diff)

            diff, _ = self.cropToBBox(diff)
            x,y = diff.shape

            match = 1 - (1/np.count_nonzero(matchingTemplate))*np.count_nonzero(diff)

            return (True, match)
        else:
            #no match found
            return (False, None)
            