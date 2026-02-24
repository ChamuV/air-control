import cv2
import mediapipe as mp
import time

mp_hands = mp.solutions.hands # detect hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
# camera resolution
cap.set(3, 1280) # set picture resolution, where 3 is width identifier
cap.set(4, 720) # height identifier 
def main():
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
        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord("q"): # adding exit key
            break

    # release capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()