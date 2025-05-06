import cv2
import numpy as np
import mediapipe as mp
import math
from collections import deque

# --- MediaPipe hands setup (looser detection for low light) ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,   # lower to pick up faint hands
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# --- Video capture & canvas ---
cap = cv2.VideoCapture(0)
canvas = None

# --- Brush slider setup ---
window_name = "Finger Paint"
cv2.namedWindow(window_name)
max_brush = 100
init_brush = 10
def nothing(x): pass
cv2.createTrackbar("BrushSize", window_name, init_brush, max_brush, nothing)

# --- State variables & smoothing buffers ---
prev_pt = None
prev_erase_pt = None
wrist_x_hist = deque(maxlen=15)
idx_hist = deque(maxlen=5)   # for index‐tip smoothing

# pre‐create CLAHE operator
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

def finger_status(landmarks, hand_label):
    tips = {'thumb':4, 'index':8, 'middle':12, 'ring':16, 'pinky':20}
    dips =  {'thumb':3, 'index':7, 'middle':11, 'ring':15, 'pinky':19}
    status = {}
    for f in tips:
        tip = landmarks[tips[f]]
        dip = landmarks[dips[f]]
        if f != 'thumb':
            status[f] = tip.y < dip.y
        else:
            # thumb direction flip per handedness
            status['thumb'] = (tip.x > dip.x) if hand_label=='Right' else (tip.x < dip.x)
    return status

def detect_wave():
    if len(wrist_x_hist) < wrist_x_hist.maxlen:
        return False
    return (max(wrist_x_hist) - min(wrist_x_hist)) > 0.3

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # initialize canvas once
    if canvas is None:
        canvas = np.zeros_like(frame)

    # 1) normalize lighting via CLAHE on Y channel
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    yuv[:,:,0] = clahe.apply(yuv[:,:,0])
    proc = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    # 2) read brush size
    brush_size = max(1, cv2.getTrackbarPos("BrushSize", window_name))

    # 3) process with MediaPipe
    rgb = cv2.cvtColor(proc, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        hand_label = results.multi_handedness[0].classification[0].label
        lm = hand_landmarks.landmark

        # record wrist x for wave detection
        wrist_x_hist.append(lm[0].x)

        # raw pixel coords
        raw_ix, raw_iy = int(lm[8].x*w), int(lm[8].y*h)
        raw_tx, raw_ty = int(lm[4].x*w), int(lm[4].y*h)

        # 3) smoothing index‐tip
        idx_hist.append((raw_ix, raw_iy))
        sx = int(sum(p[0] for p in idx_hist)/len(idx_hist))
        sy = int(sum(p[1] for p in idx_hist)/len(idx_hist))

        status = finger_status(lm, hand_label)
        index_up, middle_up, thumb_up = status['index'], status['middle'], status['thumb']

        # clear on wave
        if detect_wave():
            canvas[:] = 0

        # DRAW MODE: index up, middle down
        if index_up and not middle_up:
            color = (0,0,255)
            if prev_pt is None:
                prev_pt = (sx, sy)
            # only draw if moved enough
            if math.hypot(sx-prev_pt[0], sy-prev_pt[1]) > 2:
                cv2.line(canvas, prev_pt, (sx, sy), color, brush_size)
                prev_pt = (sx, sy)
            prev_erase_pt = None

        # ERASER MODE: only thumb up
        elif thumb_up and not (index_up or middle_up):
            color = (0,0,0)
            if prev_erase_pt is None:
                prev_erase_pt = (raw_tx, raw_ty)
            if math.hypot(raw_tx-prev_erase_pt[0], raw_ty-prev_erase_pt[1]) > 2:
                cv2.line(canvas, prev_erase_pt, (raw_tx, raw_ty), color, brush_size)
                prev_erase_pt = (raw_tx, raw_ty)
            prev_pt = None

        else:
            prev_pt = None
            prev_erase_pt = None

        # draw cursor circle at active point
        cx, cy = (sx, sy) if index_up and not middle_up else (raw_tx, raw_ty)
        cv2.circle(frame, (cx, cy), brush_size,
                   (0,255,0) if index_up else (200,200,200), 2)

    # blend & overlay UI
    output = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    cv2.putText(output, f'Brush: {brush_size}px', (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow(window_name, output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
