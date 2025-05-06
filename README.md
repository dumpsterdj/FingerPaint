# ✋🎨 Finger Paint - Hand Gesture Drawing App

This is a **gesture-controlled drawing application** that allows you to paint or erase on a virtual canvas using your webcam and hand gestures — no mouse or touch input needed!

Built using:
- 🧠 [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands) for gesture tracking
- 🎥 OpenCV for webcam input and drawing
- 🖌️ CLAHE-based lighting normalization for better performance in low light

---

## 🔧 Features

- ✋ **Draw with your index finger**
- 👍 **Erase using only your thumb**
- 🌊 **Wave gesture to clear the canvas**
- 🎛️ **Adjustable brush size via slider**
- 🕶️ **Smooth drawing and CLAHE-enhanced lighting correction**
- 📏 **Gesture smoothing to reduce jitter**

---

## 🖐️ Gesture Controls

| Gesture                           | Action                  |
|----------------------------------|-------------------------|
| Index up, Middle down            | Draw in red             |
| Only Thumb up                    | Erase with black        |
| Side-to-side wrist motion (wave) | Clear the entire canvas |

---

## 🖥️ Requirements

Install Python 3.7+ and the following packages:

```bash
pip install opencv-python mediapipe numpy
````

---

## 🚀 How to Run

1. Save the script in a file, e.g. `finger_paint.py`
2. Run the script:

```bash
python finger_paint.py
```

3. The webcam window will open. Use hand gestures to draw, erase, and clear.
4. Press `q` to quit.

---

## 🎛️ Controls

* Adjust **brush size** using the trackbar at the top of the window.
* Real-time overlay will show your brush location and size.

---

## ⚙️ How It Works

* The app uses MediaPipe to detect the hand and landmarks.
* CLAHE (Contrast Limited Adaptive Histogram Equalization) is applied to normalize lighting.
* Finger status (up/down) is calculated using landmark positions.
* Gestures are interpreted to switch between:

  * **Draw mode** (index up)
  * **Erase mode** (only thumb up)
  * **Clear command** (wave using wrist movement)
* A smoothed cursor is rendered for accurate drawing.

---

## 🧠 Enhancements Ideas

* 🎨 Add color palette switching with 2-5 fingers
* 🔄 Add undo/redo gesture support
* 👥 Multi-hand detection for collaborative drawing
* 💾 Save canvas with keyboard shortcut

---

## 📜 License

MIT License. Free to use, modify, and share with attribution.

---

## 🙌 Acknowledgments

* [MediaPipe](https://mediapipe.dev/)
* [OpenCV](https://opencv.org/)
* Inspired by natural gesture interaction and computer vision UI concepts
