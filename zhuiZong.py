import _thread

import cv2
import sys


class TrackStart():
    def __init__(self):
        tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        tracker_type = tracker_types[4]

        if tracker_type == 'BOOSTING':
            self.tracker = cv2.TrackerBoosting_create()
        elif tracker_type == 'MIL':
            self.tracker = cv2.TrackerMIL_create()
        elif tracker_type == 'KCF':
            self.tracker = cv2.TrackerKCF_create()
        elif tracker_type == 'TLD':
            self.tracker = cv2.TrackerTLD_create()
        elif tracker_type == 'MEDIANFLOW':
            self.tracker = cv2.TrackerMedianFlow_create()
        elif tracker_type == 'GOTURN':
            self.tracker = cv2.TrackerGOTURN_create()

        # Read video
        self.video = cv2.VideoCapture('testvideo.mp4')

        # Exit if video not opened.
        if not self.video.isOpened():
            print("Could not open video")
            sys.exit()

        # Define an initial bounding box
        self.bbox = (287, 23, 86, 320)  # 横，纵，宽，高

        _thread.start_new_thread(self.track_thread, ())

    def track_thread(self):
        # Read first frame.
        ok, frame_hand = self.video.read()
        if not ok:
            print('Cannot read video file')
            sys.exit()

        frame_hand = cv2.resize(frame_hand, (640, 360))
        frame_hand = frame_hand[0:360, 80:560]
        # Uncomment the line below to select a different bounding box
        self.bbox = cv2.selectROI(frame_hand, False, False)
        print(self.bbox)

        # Initialize tracker with first frame and bounding box
        ok = self.tracker.init(frame_hand, self.bbox)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, 30, (480, 360))
        while True:
            # Read a new frame
            ok, frame_hand = self.video.read()
            if not ok:
                break

            frame_hand = cv2.resize(frame_hand, (640, 360))
            frame_hand = frame_hand[0:360, 80:560]
            # Start timer
            timer = cv2.getTickCount()

            # Update tracker
            ok, self.bbox = self.tracker.update(frame_hand)

            # print(bbox)

            # Calculate Frames per second (FPS)
            fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer))

            height, width = frame_hand.shape[:2]
            # print(height, width)
            p_x = int(self.bbox[0])
            p_y = int(self.bbox[1])
            p_w = int(self.bbox[2])
            p_h = int(self.bbox[3])
            p1 = (p_x, p_y)
            p2 = (p_x + p_w, p_y + p_h)
            c_x = int(self.bbox[0] + self.bbox[2] / 2)
            c_y = int(self.bbox[1] + self.bbox[3] / 2)
            proportion_x = -(0.5 - c_x / width)
            proportion_y = -(0.5 - c_y / height)

            if ok:
                # Tracking success
                # p1 = (int(bbox[0] + (bbox[2] / 2)), int(bbox[1] + (bbox[3] / 2)))
                cv2.rectangle(frame_hand, p1, p2, (255, 255, 255), 2, 1)
                cv2.rectangle(frame_hand, p1, p2, (0, 0, 0), 1, 1)
                cv2.circle(frame_hand, (c_x, c_y), 1, (0, 0, 255), 2, 0)
                cv2.line(frame_hand, (0, c_y), (c_x - int(p_w / 2), c_y), (255, 255, 255), 2, 0)
                cv2.line(frame_hand, (0, c_y), (c_x - int(p_w / 2), c_y), (0, 0, 0), 1, 0)
                cv2.line(frame_hand, (c_x, 0), (c_x, c_y - int(p_h / 2)), (255, 255, 255), 2, 0)
                cv2.line(frame_hand, (c_x, 0), (c_x, c_y - int(p_h / 2)), (0, 0, 0), 1, 0)
                cv2.line(frame_hand, (c_x + int(p_w / 2), c_y), (width, c_y), (255, 255, 255), 2, 0)
                cv2.line(frame_hand, (c_x + int(p_w / 2), c_y), (width, c_y), (0, 0, 0), 1, 0)
                cv2.line(frame_hand, (c_x, c_y + int(p_h / 2)), (c_x, height), (255, 255, 255), 2, 0)
                cv2.line(frame_hand, (c_x, c_y + int(p_h / 2)), (c_x, height), (0, 0, 0), 1, 0)

                cv2.putText(frame_hand, "[%.2f, %.2f]" % (proportion_x, proportion_y),
                            (int(c_x + 5), int(p_y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                # Tracking failure
                cv2.putText(frame_hand, "Tracking failure detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                            (0, 0, 255), 2)

            cv2.putText(frame_hand, "FPS : " + str(fps),
                        (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame_hand, "FPS : " + str(fps),
                        (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.putText(frame_hand,
                        "Center : (" + str(c_x) + ',' + str(c_y) + ")",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame_hand,
                        "Center : (" + str(c_x) + ',' + str(c_y) + ")",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.putText(frame_hand, "Size : " + str(p_w * p_h),
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(frame_hand, "Size : " + str(p_w * p_h),
                        (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            out.write(frame_hand)

            # Display result
            cv2.imshow("Tracking", frame_hand)

            # Exit if ESC pressed
            k = cv2.waitKey(1) & 0xff
            if k == 27: break


if __name__ == '__main__':
    TrackStart()
