#!/usr/bin/env python3

import time
from time import sleep
import os
import sys
import subprocess
from threading import Barrier
# from threading import Thread
import pifacecommon
import pifacecad
import picamera

PY3 = sys.version_info[0] >= 3
if not PY3:
    print("This program only works with python3.")
    sys.exit(1)

# CONSTANTS

# Commands
# This path directs the images to the correct folder for saving.
PHOTO_PATH = "/home/pi/Documents/Python\ Projects/TimeCapture/Stills/img"
SLOWMO_PATH = "/home/pi/Documents/Python\ Projects/TimeCapture/Slow\ Motion/slowmo"
TIMELAPSE = "/home/pi/Documents/Python Projects/TimeCapture/Timelapse/"
TIMELAPSE2 = "/home/pi/Documents/Python\ Projects/TimeCapture/Timelapse/"
VIDEOPATH = "/home/pi/Documents/Python Projects/TimeCapture/Video/vid"

# The initialise function sets up the PiFaceCAD and presents the
# user with a menu of options.  This can be called whenever required.
def initialise_cad():
    cad.lcd.blink_off()
    cad.lcd.cursor_off()
    cad.lcd.backlight_on()
    cad.lcd.clear()
    cad.lcd.write("Welcome to iSpy...")
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("A-Take Photo    ")
    sleep(2)
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("B-Slow motion   ")
    sleep(2)
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("C-Timelapse     ")
    sleep(2)
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("D-Take Video    ")
    sleep(2)
    cad.lcd.set_cursor(0,1)
    cad.lcd.write("E-Exit/Shutdown ")
    sleep(2)
    cad.lcd.set_cursor(0,1)
    cad.lcd.clear()
    

# The run command function calls the command as a passed parameter and
# takes the photo using the take_photo command line arguement from raspistill
# this could also have been achieved using the python picamera library
# this way was chosen as it offered more options during the early days of the
# picamera when the python library offered less flexibility/parameters.
# I will probably rewrite this aspect of the progam at some point as an
# alternative example.

def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode('utf-8')

# This procedure takes the still
def take_still(object):
    # Clear the screen and let the user know that a still is about to be taken
    cad.lcd.clear()
    cad.lcd.write("Taking Photo...")

    # get the time in yyyy-mm-dd-hh:mm:ss format
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
    # make the image filename: imgyyyy-mm-dd-hh:mm:ss.jpg and
    # add it onto the path from the root directory.
    filename = PHOTO_PATH + timestamp + ".jpg"
    # print the filename for testing purposes to the terminal
    print("The filename is: {}." .format(filename))
    
    # Setup the take_photo command

    # Raspistill Parameters
    #
    # -vf  : vertical flip
    # -hf  : hoizontal flip
    # -w : width set to 1024
    # -h : height set to 768
    # -o : output file name appends onto the preset path e.g. imgyyyy-mm-dd-hh:mm:ss.jpg
    #
    # *** More options available at: https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
    #   

    # concatentate the command together
    take_photo = "raspistill -vf -hf -w 1024 -h 768 -o " + filename

    # run the take photo command - what does the [:-1] part mean?
    run_cmd(take_photo) 

    # Inform the user that the photo has been taken
    cad.lcd.clear()
    cad.lcd.write("Photo taken:\n{}" .format(timestamp))
    sleep(3)
    cad.lcd.clear()

    # Call Initialise_cad to present the user with the options menu again.
    initialise_cad()


def timelapse_capture(self):
    #This procedure is used to capture timelapse stills
    cad.lcd.write('Capturing\nPhotos...')
    sleep(3)
    cad.lcd.clear()
    #cad.lcd.write("Press C to stop")
    VIDEO_DAYS = 1
    FRAMES_PER_HOUR = 360
    FRAMES = FRAMES_PER_HOUR * 24 * VIDEO_DAYS
    timestamp = time.strftime("%y-%m-%d-%H-%M") # Note: note the same timestamp as before
    frame = 0

    # make a new directory to store the images in.
    newdir = TIMELAPSE + timestamp
    newdir2 = TIMELAPSE2 + timestamp
    print(newdir2)
    os.system("mkdir " + newdir2)
    sleep(5)

    def capture_frame(frame):
        with picamera.PiCamera() as cam:
            cam.vflip = True
            cam.hflip = True
            time.sleep(2)
            #cam.capture(TIMELAPSE +'{}%04d.jpg' .format(timestamp) % frame, resize=(720, 576))
            cam.capture(newdir + '/timelapse-%04d.jpg' % frame, resize=(720, 576))
            
    while cad.switches[4].value==0:
        start = time.time()
        cad.lcd.write("Capturing still\nPress E to stop")
        capture_frame(frame)
        frame = frame +1
        cad.lcd.clear()
        sleep(
            int(60 * 60 / FRAMES_PER_HOUR) - (time.time() - start)
        )
    

    if cad.switches[4].value == 1:
        cad.lcd.clear()
        cad.lcd.write('Exit pressed')
        sleep(2)

    cad.lcd.clear()
    cad.lcd.write("Creating Video Now")
    sleep(2)
    cad.lcd.clear
    cad.lcd.write("Exporting File List")
    sleep(2)
    encode_video = "avconv -framerate 25 -f image2 -i " + newdir2 + "/timelapse-%04d.jpg -b 65536k " + newdir2 + "/timelapse.mov"
    print(encode_video)
    cad.lcd.clear()
    cad.lcd.write("Encoding Video\nDo not disturb")
    os.system(encode_video)
    
    initialise_cad()
    sleep(2)

#This procedure records video when the B button is pressed.
def capture_video(self):

    #get the current time to append to the filename
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
    cad.lcd.clear()
    cad.lcd.write('Recording-Button\nE to Stop...')
    with picamera.PiCamera() as cam:
        cam.vflip = True
        cam.hflip = True
        cam.start_recording(VIDEOPATH + timestamp +'.h264')
        stop_pressed = 0
        recordingtime = 0

        while cad.switches[4].value == 0:
            sleep(2)
            recordingtime = recordingtime + 2
            cad.lcd.clear()
            cad.lcd.write('Recording...\n {0} seconds.' .format(recordingtime))

            if cad.switches[4].value == 1:
                cam.stop_recording()
                cad.lcd.write('Recording Stopped')
                sleep(1)
                break

    cad.lcd.clear()
    cad.lcd.write("The video\nwas stopped.")
    cad.switches[4].value = 0
    sleep(2)
            

# This procedure captures a 10 second slowmotion video
def slow_motion(object):
    cad.lcd.clear()
    cad.lcd.write("Starting 10sec\nSlowMotion Now..")
    sleep(2)

    ##### Record the slow motion video #####

    cad.lcd.clear()
    cad.lcd.write("Recording...\n10 seconds")
    os.system("raspivid -vf -hf -w 640 -h 480 -fps 90 -t 10000 -o vid.h264")
    sleep(2)

    ##### Convert the raw video file to playable mp4 #####
    cad.lcd.clear()
    cad.lcd.write("Converting video\nPlease wait...")

    # get the time in yyyy-mm-dd-hh:mm:ss format
    timestamp = time.strftime("%Y-%m-%d-%H:%M:%S")
    # make the image filename: imgyyyy-mm-dd-hh:mm:ss.jpg and
    # add it onto the path from the root directory.
    filename = SLOWMO_PATH + timestamp + ".mp4"
    # print the filename for testing purposes to the terminal
    cad.lcd.write("The filename is:\n{}." .format(filename))

    os.system("MP4Box -add vid.h264 " + filename)

    cad.lcd.clear()
    cad.lcd.write("Conversion\nComplete...")
    sleep(2)
    initialise_cad()


# This procedure informs the user and prepares the program for shutdown
def close():
    cad.lcd.clear()
    cad.lcd.write("iSpy is shutting\ndown.")
    sleep(3)
    cad.lcd.clear()
    cad.lcd.backlight_off()
    #exit the program
    sys.exit(0)

# Start of the main program here
if __name__ == "__main__":

    # create a global object called cad so the PiFaceCAD can be referred to
    # anywhere throughout the program.
    global cad
    cad = pifacecad.PiFaceCAD() # create an instance of this object
    
    initialise_cad() # call the initialise_cad function and display the menu

    # As per the PiFaceCAD examples, the listener cannot deactivate itself so
    # we have to wait until it has finished using a barrier.
    global end_barrier # allow this to be an object which can be referred to anywhere in the program
    end_barrier = Barrier(2) # create the instance of Barrier
    
    # setup the button presses by creating an object called switchlistener
    # NOTE - switchlistener will not run in IDLE3 but needs to be executed in
    # a terminal window.  Set the Chmod to 0777
    switchlistener = pifacecad.SwitchEventListener(chip=cad)
    switchlistener.register(0, pifacecad.IODIR_ON, take_still)
    switchlistener.register(1, pifacecad.IODIR_ON, slow_motion)
    switchlistener.register(2, pifacecad.IODIR_ON, timelapse_capture)
    switchlistener.register(3, pifacecad.IODIR_ON, capture_video)


    # setup the exit button
    switchlistener.register(4, pifacecad.IODIR_ON, end_barrier.wait)

    # start polling the switches until the end_barrier switch has been pressed.
    switchlistener.activate()
    
    end_barrier.wait()  # wait until exit
    switchlistener.deactivate() # deactivate the switchlistener i.e. stop polling the switches for activity.
    close() # run the close function
    
