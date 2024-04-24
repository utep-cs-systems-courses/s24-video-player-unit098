#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue
import threading


class lq:
    def __init__(self, limit):
        self.insem = threading.Semaphore(limit)
        self.outsem = threading.Semaphore(0)
        self.mu = threading.Lock()
        self.q = queue.Queue()
        
    def put(self, item):
        self.insem.acquire()
        self.mu.acquire()
        self.q.put(item)
        self.mu.release()
        self.outsem.release()
        print(self.outsem._value)
    
    def get(self):
        self.outsem.acquire()
        self.mu.acquire()
        outp = self.q.get()
        self.mu.release()
        self.insem.release()
        return outp
        
def extractFrames(fileName, outputBuffer, maxFramesToLoad=9999):
    # Initialize frame count 
    count = 0

    # open video file
    vidcap = cv2.VideoCapture(fileName)

    # read first image
    success,image = vidcap.read()
    
    print(f'Reading frame {count} {success}')
    while success and count < maxFramesToLoad:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame as base 64 to make debugging easier
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputBuffer.put(image)
       
        success,image = vidcap.read()
        print(f'Reading frame {count} {success}')
        count += 1
    outputBuffer.put('&')
    print('Frame extraction complete')

def makeGrey(inputBuffer, outputBuffer):
    count = 0
    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        frame = inputBuffer.get()
        if(frame == '&'):
            outputBuffer.put('&')
            break

        print(f'greifying frame {count}')        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        outputBuffer.put(grayscaleFrame)

        count += 1

    print('Finished greyifying all frames')

def displayFrames(inputBuffer):
    # initialize frame count
    count = 0
    # go through each frame in the buffer until the buffer is empty
    while True:
        # get the next frame
        frame = inputBuffer.get()
        if(frame == '&'):
            break

        print(f'Displaying frame {count}')        

        # display the image in a window called "video" and wait 42ms
        # before displaying the next frame
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

    print('Finished displaying all frames')
    # cleanup the windows
    cv2.destroyAllWindows()

# filename of clip to load
filename = 'clip.mp4'

# shared queue  
extractionQueue = lq(10)
greyQueue = lq(10)

# extract the frames
thread = threading.Thread(target=extractFrames, args = (filename,extractionQueue))
thread2 = threading.Thread(target=displayFrames, args = (greyQueue,))
thread3 = threading.Thread(target=makeGrey, args = (extractionQueue, greyQueue))
thread.start()
thread2.start()
thread3.start()

# display the frames





