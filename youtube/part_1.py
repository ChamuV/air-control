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
    with mp_hands.Hands(
        max_num_hands=2,
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
                    mp_draw.draw_landmarks(
                        img, # where we want to draw,
                        hand_landmarks, # what we want to draw
                        mp_hands.HAND_CONNECTIONS, # lines between hands
                    )

                    finger_tips = {
                        # each finger has 4 nodes starting from the bottom
                        "Thumb": hand_landmarks.landmark[4],
                        "Index": hand_landmarks.landmark[8],
                        "Middle": hand_landmarks.landmark[12],
                        "Ring": hand_landmarks.landmark[16],
                        "Pinky": hand_landmarks.landmark[20],
                    }

                    # loop to display name of finger
                    for name, landmark in finger_tips.items():
                        x, y = int(landmark.x * w), int(landmark.y * h)
                        cv2.putText(
                            img, # where
                            name, # name of what to put (finger)
                            (x, y - 10), # coor and -10 to lift up above finger
                            cv2.FONT_HERSHEY_SIMPLEX, # font
                            0.5, # font thickness
                            (255, 255, 255), # color,
                            1, # linetype
                        )

                        # green circle at the top of finger
                        cv2.circle(
                            img, 
                            (x, y),
                            5, 
                            (0, 255, 0),
                            -1,
                        )
            cv2.imshow("Image", img)

            if cv2.waitKey(1) & 0xFF == ord("q"): # adding exit key
                break

    # release capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()