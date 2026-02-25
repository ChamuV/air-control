import cv2
import mediapipe as mp
import pyautogui
import math
import time

mp_hands = mp.solutions.hands # detect hands
mp_draw = mp.solutions.drawing_utils

# map camera pixels to screen pixels as screen bigger
screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)
# camera resolution
cap.set(3, 640) # set picture resolution, where 3 is width identifier
cap.set(4, 480) # height identifier 

# avg the points to treat hand as a single point
PALM_IDS = [0, 5, 9, 13, 17] # bottom of the finger joints

# region to consider before moving
DEAD_ZONE = 10

# setting threshold for pinch to be satisfied
PINCH_START = 30

def main():
    prev_x, prev_y = screen_width // 2, screen_height // 2 # centre of screen - for the posn at start of program  

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    ) as hands:
        # showing camera feed
        while True: # do this to check if camera feed is loading properly
            attempt = 0
            success, img = cap.read()
            while not success and attempt < 5:
                time.sleep(0.2)
                success, img = cap.read()
                attempt += 1
            if not success:
                print("Fail to read frame")
                break
            
            # flipping img (mirror version) for easy tracking
            img = cv2.flip(img, 1)
            h,w, _ = img.shape

            # convert img to rgb from bgr due to library req
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            results = hands.process(rgb) # process img to get data

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:

                    # pinch action for selection, by looking at dist between thumb and index
                    index_tip = hand_landmarks.landmark[8]
                    thumb_tip = hand_landmarks.landmark[4]

                    cx = sum(hand_landmarks.landmark[id].x for id in PALM_IDS) / len(PALM_IDS) # find avg x
                    cy = sum(hand_landmarks.landmark[id].y for id in PALM_IDS) / len(PALM_IDS) 

                    screen_x = int(cx * screen_width)
                    screen_y = int(cy * screen_height)

                    dx = screen_x - prev_x # checking for movement from orig position
                    dy = screen_y - prev_y

                    if math.hypot(dx, dy) > DEAD_ZONE:
                        pyautogui.moveTo(screen_x, screen_y, duration=0)
                        # reset prev posn after moving beyond ignorable amount
                        prev_x = screen_x
                        prev_y = screen_y

                    ix, iy = index_tip.x, index_tip.y
                    tx, ty = thumb_tip.x, thumb_tip.y

                    ix, iy = int(ix * w), int(iy * h) # normalise with screen
                    tx, ty = int(tx * w), int(ty * h)

                    pinch_distance = math.hypot(ix - tx, iy - ty)
                    if pinch_distance < PINCH_START:
                        pyautogui.click()

            cv2.imshow("Image", img)

            if cv2.waitKey(1) & 0xFF == ord("q"): # adding exit key
                break

    # release capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()