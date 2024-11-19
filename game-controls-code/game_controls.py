"""
COMP 332 Grid-based game controls.

Name: Maggie Betts
Email: maggiebetts@sandiego.edu
Date: February 9th, 2024
"""

import pyautogui

last_position = (None,None)
last_dir = ''

def debugging(isdebugging,action,direction):
    """
    Prints the action that was used and the direction if debugging mode is on.

    Parameters:
    isdebugging (bool): indicates if the debugging mode is on
    action (str): The action that was taken depending on the mode running
    direction (str): The direction expected (e.g., up, down, left, right)

    Return: None
    """
    if isdebugging:
        print(action,"was used to go",direction)


def keypress(is_debugging):
    ''' 
    Controls a grid based game through the use of the keyboard. 
    The keymapping is as follows: x = up, x = down, x = left, x = right, x = exit

    Parameters:
    is_debugging (bool): indicates if the debugging mode is on

    Returns: None
    '''

    import keyboard

    is_running = True

    while is_running:
        if keyboard.is_pressed('w'):
            pyautogui.press('up')
            debugging(is_debugging, 'w', 'up')
        elif keyboard.is_pressed('s'):
             pyautogui.press('down')
             debugging(is_debugging, 's', 'down')
        elif keyboard.is_pressed('a'):
             pyautogui.press('left')
             debugging(is_debugging, 'a', 'left')
        elif keyboard.is_pressed('d'):
             pyautogui.press('right')
             debugging(is_debugging, 'd', 'right')
        elif keyboard.is_pressed('x'):
             pyautogui.press('exit')
             debugging(is_debugging, 'x', 'exit')


def trackpad_mouse(is_debugging):
    ''' 
    Controls a grid based game through the use of the mouse/trackpad. 

    Parameters:
    is_debugging (bool): indicates if the debugging mode is on

    Returns: None
    '''

    from pynput import mouse

    def on_move(x, y):

        global last_position
        global last_dir

        # determine how far the mouse needs to move to indicate a move
        threshold = (20, 20)

        #determine the position difference
        if last_position[0] != None and last_position[1] != None:
            position_difference = [None, None]
            position_difference[0] = last_position[0] - x
            position_difference[1] = last_position[1] - y

            #if the position changed most along the x axis
            if abs(position_difference[0]) > abs(position_difference[1]):
                if abs(position_difference[0]) > threshold[0]:
                    if position_difference[0] > 0 and last_dir != 'left':
                        pyautogui.press('left')
                        debugging(is_debugging, 'mouse', 'left')
                        last_dir = 'left'
                    elif last_dir != 'right':
                        pyautogui.press('right')
                        debugging(is_debugging, 'mouse', 'right')
                        last_dir = 'right'
            #if the position changed most along the y axis
            else:
                if abs(position_difference[1]) > threshold[1]:
                    if position_difference[1] > 0 and last_dir != 'up':
                        pyautogui.press('up')
                        debugging(is_debugging, 'mouse', 'up')
                        last_dir = 'up'
                    elif last_dir != 'down':
                        pyautogui.press('down')
                        debugging(is_debugging, 'mouse', 'down')
                        last_dir = 'down'
            
        
        last_position = (x,y)


        
    def on_click(x, y, button, pressed):
        debugging(is_debugging, 'mouse', 'exit')
        if pressed:
            return False
        

    with mouse.Listener(on_move=on_move,on_click=on_click) as listener:
        listener.join() 

def color_tracker(is_debugging):
    ''' 
    Controls a grid based game through the use of tracking a white colored object. 

    Parameters:
    is_debugging (bool): indicates if the debugging mode is on

    Returns: None
    '''

    import cv2
    import imutils
    import numpy as np
    from collections import deque
    import time
    import multithreaded_webcam as mw


    # define HSV colour range
    colorLower = np.array([0,0,168])
    colorUpper = np.array([172,111,255])

    # set the limit for the number of frames to store and the number that have seen direction change
    buffer = 20
    pts = deque(maxlen = buffer)

    # store the direction and number of frames with direction change
    num_frames = 0
    (dX, dY) = (0, 0)
    direction = ''
    global last_dir

    #Sleep for 2 seconds to let camera initialize properly
    time.sleep(2)
    #Start video capture
    vs = mw.WebcamVideoStream().start()

    is_running = True
    threshhold = (60, 60)

    while is_running:
        #get the frame, flip, and resize
        frame = vs.read()
        frame = cv2.flip(frame,1)
        frame = imutils.resize(frame, width = 600)

        #blur the frame to make color detection easier
        simplified_frame = cv2.GaussianBlur(frame, (5,5), 0)

        #convert frame color HSV to use for our limits
        color_frame = cv2.cvtColor(simplified_frame, cv2.COLOR_BGR2HSV)

        #create a mask to determine if it finds 
        color_isolate_frame = cv2.inRange(color_frame, colorLower, colorUpper)
        noise_reduced_frame = cv2.erode(color_isolate_frame, None, iterations = 2)
        masked_frame = cv2.dilate(noise_reduced_frame, None, iterations = 2)

        #determine contours of identified object
        contours, _ = cv2.findContours(masked_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        center = None

        if len(contours) > 0:
            #determine the largest contour
            max_contour = max(contours, key = cv2.contourArea)

            #get radius of contour
            coordinates, radius = cv2.minEnclosingCircle(max_contour)

            #find the center of our points
            M = cv2.moments(max_contour)
            center = (int(M['m10']/M['m00']), int(M['m01'] / M['m00']))

            if (radius > 10):
                pts.appendleft(center)
                cv2.circle(frame, (int(coordinates[0]), int(coordinates[1])), int(radius), (0, 255, 255), 2)

    
        if num_frames > 10 and len(pts) > 10:
            original_x = pts[0][0]
            original_y = pts[0][1]
            new_x = pts[-10][0]
            new_y = pts[-10][1]

            #check if the difference in movement is enough to reach the threshold
            x_difference = original_x - new_x
            y_difference = original_y - new_y

            #test against threshhold, and set direction like with mouse
            if abs(x_difference) > abs(y_difference):
                if abs(x_difference) > threshhold[0]:
                    if x_difference > 0 and last_dir != 'left':
                        pyautogui.press('left')
                        debugging(is_debugging, 'color object', 'left')
                        last_dir = 'left'
                        direction = 'left'
                    elif last_dir != 'right':
                        pyautogui.press('right')
                        debugging(is_debugging, 'color object', 'right')
                        last_dir = 'right'
                        direction = 'right'
            else:
                if abs(y_difference) > threshhold[1]:
                    if y_difference > 0 and last_dir != 'up':
                        pyautogui.press('up')
                        debugging(is_debugging, 'color object', 'up')
                        last_dir = 'up'
                        direction = 'up'
                    elif last_dir != 'down':
                        pyautogui.press('down')
                        debugging(is_debugging, 'color object', 'down')
                        last_dir = 'down'
                        direction = 'down'

        num_frames += 1


        # DO NOT EDIT BELOW THIS POINT
        #Write the detected direction on the frame.
        cv2.putText(frame, direction, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
        #Show the output frame.
        cv2.imshow('Game Control Window', frame)
        cv2.waitKey(1)

    # Close all windows and close the video stream.
    cv2.destroyAllWindows()
    vs.stop()
        



def finger_tracking(is_debugging):
    ''' 
    Controls a grid based game through the use of finger tracking 
    The finger mapping is as follows: 1 = up, 4 = down, 3 = left, 2 = right, 5 = exit

    Parameters:
    is_debugging (bool): indicates if the debugging mode is on

    Returns: None
    '''

    import cv2
    import imutils
    import numpy as np
    import time
    import multithreaded_webcam as mw
    import mediapipe as mp

    ##Sleep for 2 seconds to let camera initialize properly
    time.sleep(2)
    #Start video capture
    vs = mw.WebcamVideoStream().start()

    #Get the trained model for the hands
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False,
                      max_num_hands=1,
                      min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
    mpDraw = mp.solutions.drawing_utils

    global last_dir

    is_running = True

    while is_running:

        #get frame, flip it, resize it
        frame = vs.read()
        frame = cv2.flip(frame,1)
        frame = imutils.resize(frame, width = 600)

       
        # alter color of frame and track hands
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(color_frame)

        
        count = 0
        hand_features = []
        #if we detected a hand
        if results.multi_hand_landmarks:
            #isolate landmarks in hand detected
            for item in results.multi_hand_landmarks:
                for id, lm in enumerate(item.landmark):
                    height, width, _ = frame.shape
                    x = int(lm.x * width)
                    y = int(lm.y * height)
                    cv2.circle(frame, (x,y), 3, (255,0,255), cv2.FILLED)
                    hand_features.append((id, x, y))
                mpDraw.draw_landmarks(frame, item, mpHands.HAND_CONNECTIONS)

        #if we have detected a hand determine which fingers are raised by their positions
        if len(hand_features) != 0:
            if hand_features[4][1] < hand_features[3][1]:
                count += 1
            if hand_features[8][2] < hand_features[6][2]:
                count += 1
            if hand_features[12][2] < hand_features[10][2]:
                count += 1
            if hand_features[16][2] < hand_features[14][2]:
                count += 1
            if hand_features[20][2] < hand_features[18][2]:
                count += 1

            #based on the number of fingers, determine direction
            if count == 3 and last_dir != 'left':
                pyautogui.press('left')
                debugging(is_debugging, 'finger tracking', 'left')
                last_dir = 'left'
            elif count == 2 and last_dir != 'right':
                pyautogui.press('right')
                debugging(is_debugging, 'finger tracking', 'right')
                last_dir = 'right'
            elif count == 1 and last_dir != 'up':
                pyautogui.press('up')
                debugging(is_debugging, 'finger tracking', 'up')
                last_dir = 'up'
            elif count == 4 and last_dir != 'down':
                pyautogui.press('down')
                debugging(is_debugging, 'finger tracking', 'down')
                last_dir = 'down'
            elif count == 5:
                pyautogui.press('exit')
                debugging(is_debugging, 'finger tracking', 'exit')



        # DO NOT EDIT BELOW THIS POINT
        #Show the output frame.
        cv2.putText(frame,str(int(count)), (10,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,255), 3)
        cv2.imshow("Game Control Window", frame)
        cv2.waitKey(1)

    # Close all windows and close the video stream.
    cv2.destroyAllWindows()
    vs.stop()

def unique_control(is_debugging):
    ''' 
    Controls a grid based game through the use of speech instruction
    The speech instructions is as follows: saying "left" = left, saying "up" = up, saying "down" = down, 
    saying "right" = right, saying "exit" = exit

    Parameters:
    is_debugging (bool): indicates if the debugging mode is on

    Returns: None

    FAIR WARNING: IS EXTREMELY SLOW BUT DOES EVENTUALLY WORK
    '''

    import speech_recognition as sr
    import pyaudio

    global last_dir

    is_running = True

    while is_running:
        r = sr.Recognizer()
        
        #allow the mic to receive speech
        with sr.Microphone() as source:
            audio = r.listen(source)

        #try to interpret audio received
        try:
            query = r.recognize_google(audio)
        except Exception as e:
            print('unable to interpret')
        
        
        #depending on what was said, move that direction
        if 'left' in query and last_dir != 'left':
            pyautogui.press('left')
            debugging(is_debugging, 'voice', 'left')
            last_dir = 'left'
        elif 'right' in query and last_dir != 'right':
            pyautogui.press('right')
            debugging(is_debugging, 'voice', 'right')
            last_dir = 'right'
        elif 'up' in query and last_dir != 'up':
            pyautogui.press('up')
            debugging(is_debugging, 'voice', 'up')
            last_dir = 'up'
        elif 'down' in query and last_dir != 'down':
            pyautogui.press('down')
            debugging(is_debugging, 'voice', 'down')
            last_dir = 'down'
        elif 'exit' in query:
            pyautogui.press('exit')
            debugging(is_debugging, 'voice', 'exit')
            last_dir = 'exit'
        



def main():
    is_debugging = False
    debug_quiry = input('Would you like to print the direction you are going while running the game (y or n)? ')
    if debug_quiry == 'y':
        is_debugging = True
        print("Printing in now turned on!")
    control_mode = input("How would you like to control the game?\n\tPress 1 for keyboard\n\tPress 2 for the mouse/trackpad\n\tPress 3 for the color tracker\n\tPress 4 for the finger tracker\n\tPress 5 for the unique tracker\n")
    if control_mode == '1':
        keypress(is_debugging)
    elif control_mode == '2':
        trackpad_mouse(is_debugging)
    elif control_mode == '3':
        color_tracker(is_debugging)
    elif control_mode == '4':
        finger_tracking(is_debugging)
    elif control_mode == '5':
        unique_control(is_debugging)

if __name__ == '__main__':
	main()
