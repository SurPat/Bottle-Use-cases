from __future__ import print_function
import sys
import cv2
import imutils; import time
import numpy as np

def rescale_frame(frame, percent=80):  # make the video windows a bit smaller
            width = int(frame.shape[1] * percent / 100)
            height = int(frame.shape[0] * percent / 100)
            dim = (width, height)
            return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

def Liquid_Level_Inspection(frame):
    start_time = time.time()
        #print("Liquid Level Inspection")
    try:
        frame = rescale_frame(frame)
        out_new = np.uint8(frame)
        out_Gray = cv2.cvtColor(out_new, cv2.COLOR_BGR2GRAY)
        ret, thresh_out = cv2.threshold(out_Gray, 30, 255, cv2.THRESH_BINARY_INV)
        kernel_ip = np.ones((2, 2), np.uint8)
        eroded_ip = cv2.erode(thresh_out, kernel_ip, iterations=1)
        dilated_ip = cv2.dilate(eroded_ip, kernel_ip, iterations=1)
        #cv2.imshow("dileted", dilated_ip)
        #             cv2.imshow("testing 222", dilated_ip)
        cnts = cv2.findContours(dilated_ip.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        #     print(len(cnts))

        if len(cnts) == 0:
            flag_empty = 1

            flag_detected = 0
            #         text = "Empty Frame"
            #         cv2.putText(frame, text, (25,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),2)
            cv2.imshow("Decision", frame)

        # read image and take first channel only
        # img = cv2.imread("half with cap.jpg")
        #     img = cv2.imread("stick.jpg")
        bottle_gray = cv2.cvtColor(out_new, cv2.COLOR_BGR2GRAY)
        # bottle_gray = cv2.split(bottle_3_channel)[0]
        #     cv2.imshow("Bottle Gray", bottle_gray)
        # cv2.waitKey(0)

        # blur image
        bottle_gray = cv2.GaussianBlur(bottle_gray, (7, 7), 0)
        #     cv2.imshow("Bottle Gray Smoothed 7 x 7", bottle_gray)
        # cv2.waitKey(0)
        # draw histogram
        # plt.hist(bottle_gray.ravel(), 256,[0, 256]); plt.show()

        # manual threshold
        bottle_gray = np.uint8(bottle_gray)
        bottle_threshold = cv2.threshold(bottle_gray, 50, 255, cv2.THRESH_BINARY_INV)[1]
        bottle_threshold = np.uint8(bottle_threshold)
        #     cv2.imshow("Bottle Gray Threshold 27.5", bottle_threshold)
        # cv2.waitKey(0)

        # apply opening operation
        kernel_O = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        bottle_open = cv2.morphologyEx(bottle_threshold, cv2.MORPH_OPEN, kernel_O, 3)
        kernel_C = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        bottle_close = cv2.morphologyEx(bottle_open, cv2.MORPH_CLOSE, kernel_C, 3)
        cv2.imshow("Contour", bottle_close)

        # cv2.waitKey(0)

        # find all contours
        contours = cv2.findContours(bottle_close.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        bottle_clone = out_new.copy()
        cv2.drawContours(bottle_clone, contours, -1, (0, 255, 0), 2)
        cv2.imshow("All Contours", bottle_clone)
        # cv2.waitKey(0)

        # sort contours by area
        areas = [cv2.contourArea(contour) for contour in contours]
        if len(areas) == 0:
            cv2.imshow("Decision", frame)
        (contours, areas) = zip(*sorted(zip(contours, areas), key=lambda a: a[1]))
        # print contour with largest area
        bottle_clone = out_new.copy()
        cv2.drawContours(bottle_clone, [contours[-1]], -1, (0, 255, 0), 2)
        cv2.imshow("Largest contour", bottle_clone)
        # cv2.waitKey(0)

        # draw bounding box, calculate aspect and display decision
        bottle_clone = out_new.copy()
        (x, y, w, h) = cv2.boundingRect(contours[-1])
        print("value of x y w h",x, y, w, h)
        aspectRatio = w / float(h)
        print("aspect ratio: ",aspectRatio)

        if (1.4 < aspectRatio < 1.6):
            cv2.putText(bottle_clone, "Too Low", (x + 60, y + 100), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 255), 2)
            frame_time = (time.time() - start_time)
            print("-----{0} seconds---".format(frame_time))
            FPS = 1 / frame_time
            print("FPS: ", FPS)
            FPS_str = "FPS = {0}".format(str(FPS))
            cv2.putText(bottle_clone, FPS_str, (900, 900), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            cv2.imshow("Decision", bottle_clone)
            print("TOO LOW RATIO: ", aspectRatio)
            #self.displayImage2(bottle_clone, 1)
        elif (1.65 < aspectRatio < 4.0):
                #     if ( h > 150):
            cv2.rectangle(bottle_clone, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(bottle_clone, "Low", (x + 60, y + 100), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 0, 255), 2)
            frame_time = (time.time() - start_time)
            print("-----{0} seconds---".format(frame_time))
            FPS = 1 / frame_time
            print("FPS: ", FPS)
            FPS_str = "FPS = {0}".format(str(FPS))
            cv2.putText(bottle_clone, FPS_str, (900, 900), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            print("LOW RATIO: ", aspectRatio)
            cv2.imshow("Decision", bottle_clone)
                        #     elif( y+h> 155):
            #
        else:
            cv2.rectangle(bottle_clone, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(bottle_clone, "Full", (x + 60, y + 100), cv2.FONT_HERSHEY_PLAIN, 2.5, (0, 255, 0), 2)
            frame_time = (time.time() - start_time)
            print("-----{0} seconds---".format(frame_time))
            FPS = 1 / frame_time
            print("FPS: ", FPS)
            FPS_str = "FPS = {0}".format(str(FPS))
            cv2.putText(bottle_clone, FPS_str, (900, 900), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            print("FULL RATIO: ", aspectRatio)
            cv2.imshow("Decision", bottle_clone)
            return bottle_clone
            #self.displayImage2(bottle_clone, 1)

    except:
        print("no contours...")
        cv2.putText(frame, "No contours", (900, 900), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
        cv2.imshow("Decision", frame)



    