# Intrusion Detection System

This project implements an Intrusion Detection System using computer vision techniques. The system allows the user to define a region of interest (ROI) on a video feed, and it detects any intrusion within that region. The system highlights the ROI, tracks motion, and raises an alarm when an intrusion is detected.

## Features

- User-friendly GUI for selecting and visualizing the ROI.
- Motion detection within the defined ROI.
- Real-time display of video feed with ROI and intrusion detection overlays.
- Audio alarm when an intrusion is detected.

## Requirements

- Python 3.7+
- OpenCV 4.5+
- PyQt5
- imutils
- numpy
- winsound (Windows-only, for audio alarm)

## Installation

1. Clone the repository:

2. Create and activate a virtual environment (optional but recommended):

3. Install the required dependencies:

4. Run the application:


## Instructions

1. Launch the application by running `python main.py -f <video_path or camera_path>`.

2. The application window will open, displaying the video feed from the default camera.

3. To define the ROI, click and drag the left mouse button to create a polygon shape. Release the mouse button to complete the shape. You can create multiple polygons for complex ROIs.

4. To remove the last defined ROI, right-click the mouse.

5. Press the Esc key to reset the ROI and start anew.

6. The application will track motion within the defined ROI. If an intrusion is detected, the ROI will be highlighted in red, and an audio alarm will be raised.

7. To exit the application, close the window or press Ctrl+C in the terminal.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.