import tkinter as tk
import cv2
import time
import PIL
from PIL import ImageTk
import gaze_tracking
import csv
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import patientWindow as pw
import userWindow as uw


class App: #I show the webcam output
    def __init__(self, window, window_title, id, old_window,video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.PatientId = id
        self.old_window = old_window
        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True)

        self.btn_stop = tk.Button(window, text="STOP RECORDING", width=50, command=self.stop)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            cv2.imwrite("data/snapshots/frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg",
                        cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def stop(self):
        self.window.destroy()
        self.vid.__del__()
        pw.PatientWindow(self.old_window, self.PatientId)
        #newWindow = uw.userWindow("Vito", "De Feo", 1234)
        #newWindow.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)


class Faceless_app: # I show just a 'Stop record' Button
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)
        self.btn_stop = tk.Button(window, text="STOP RECORDING", width=50, command=self.stop)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)
        self.delay = 10
        self.update()

    def stop(self):
        self.window.destroy()
        self.vid.__del__()

    def update(self):
        # Get a frame from the video source

        self.vid.get_frame()
        self.window.after(self.delay, self.update)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        self.gaze = gaze_tracking.GazeTracking()
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.coordinates = []

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            # add features to webcam input
            self.gaze.refresh(frame)
            frame = self.gaze.annotated_frame()

            if ret:
                left_pupil = self.gaze.pupil_left_coords()
                right_pupil = self.gaze.pupil_right_coords()
                if (left_pupil is not None) & (right_pupil is not None):
                    self.coordinates.append([left_pupil[0], left_pupil[1],right_pupil[0], right_pupil[1]])

                cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                            (147, 58, 31), 1)
                cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9,
                            (147, 58, 31), 1)

                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            raise ValueError("Unable to get a frame")

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            fieldnames = ['left_pupil_x', 'left_pupil_y', 'right_pupil_x', 'right_pupil_y']

            my_df = pd.DataFrame(self.coordinates, columns=fieldnames)
            my_df.to_csv('test.csv', index=False, header=True)

            #heatmap in the end of the use of the camera
            x, y = my_df["left_pupil_x"], my_df["left_pupil_y"]
            plt.hist2d(x, y, bins=(50, 50), cmap=plt.cm.jet)
            plt.savefig('heatmap.png')
            #data/id/heatmap.png
            self.vid.release()

#App(tk.Tk(), "Tkinter and OpenCV")
