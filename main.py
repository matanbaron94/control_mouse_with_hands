import time
import cv2
from pynput.mouse import Button, Controller
import winsound
import mediapipe as mp
import settings



distance = settings.distance

click_sensitivity = settings.click_sensitivity


n = True
status = True
mouse = Controller()

_x = 0
_y = 0

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


mp_drawing2 = mp.solutions.drawing_utils
mp_drawing_styles2 = mp.solutions.drawing_styles
mp_hands2 = mp.solutions.hands


cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands = 1,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

  while cap.isOpened():
    success, image = cap.read()
    image2 = image
    cropped_image = image2[120:360, 180:470]
    image2 = cv2.resize(cropped_image, (0, 0), fx=4, fy=4)

    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
          image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())


      m = results.multi_handedness[0].classification[0]
      if m.index == 0:
        n = True
      if m.index == 1:
        n =False

      x1 = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x
      y1 = results.multi_hand_landmarks[0].landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y

      x1 = (-x1*30) +30
      y1= y1*30

      if x1 >20:
        status= False
        print("lock mode")
      if x1<10:
        status= True
        print("Active mode")
      if 10<=x1<=20:
        _x = x1-10
        _x = _x * (settings.monitor_width / 10)
      if 10 <= y1 <= 20:
        _y = y1 - 10
        _y = _y * (settings.monitor_height / 10)

      p = (int(_x),int(_y))
      time.sleep(0.05)
      # print(f"p={p} ---- r={int(x1),int(y1)} ----- s={status} ---- l={m.label}")

      if status == True:
        if n == True:
          mouse.position = p
    if settings.hide_camview == False:
      cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))


  #------------

    with mp_hands2.Hands(
            max_num_hands=1,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands2:

      success, image2 = cap.read()

      cropped_image = image2[120:360, 180:470]
      image2 = cv2.resize(cropped_image, (0, 0), fx=2, fy=2)

      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue

      image2.flags.writeable = False
      image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
      results = hands2.process(image2)
      image2.flags.writeable = True
      image2 = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)

      if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
          mp_drawing2.draw_landmarks(
            image2,
            hand_landmarks,
            mp_hands2.HAND_CONNECTIONS,
            mp_drawing_styles2.get_default_hand_landmarks_style(),
            mp_drawing_styles2.get_default_hand_connections_style())

        cx1 = hand_landmarks.landmark[mp_hands2.HandLandmark.INDEX_FINGER_TIP].x * settings.monitor_width
        cy1 = hand_landmarks.landmark[mp_hands2.HandLandmark.INDEX_FINGER_TIP].y * settings.monitor_height

        cx2 = hand_landmarks.landmark[mp_hands2.HandLandmark.THUMB_TIP].x * settings.monitor_width
        cy2 = hand_landmarks.landmark[mp_hands2.HandLandmark.THUMB_TIP].y * settings.monitor_height

        if status == True:
          if n == True:
            if (cy2 > cy1) and (cy2 - 9*settings.click_sensitivity < cy1):
              if (cx2 + 40 > cx1) and (cx2 - 16*settings.click_sensitivity < cx1):
                mouse.press(Button.left)
                mouse.release(Button.left)
                if settings.mute == False:
                  filename = "docs/click_sound.wav"
                  winsound.PlaySound(filename, winsound.SND_FILENAME)
                print("Left click")
                time.sleep(0.05)

    if settings.hide_camview == False:
      cv2.imshow('Zoom', cv2.flip(image2, 1))


    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
