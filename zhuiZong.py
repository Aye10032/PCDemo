import cv2
import sys

(major_ver, minor_ver, subminor_ver) = cv2.__version__.split('.')

if __name__ == '__main__':

    # Set up tracker.
    # Instead of MIL, you can also use

    tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
    tracker_type = tracker_types[4]

    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()

    # Read video
    video = cv2.VideoCapture('target2.mp4')

    # Exit if video not opened.
    if not video.isOpened():
        print("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print('Cannot read video file')
        sys.exit()

    frame = cv2.resize(frame, (720, 480))
    # Define an initial bounding box
    bbox = (287, 23, 86, 320) # 横，纵，宽，高

    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False, False)
    print(bbox)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 60, (720, 480))

    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        frame = cv2.resize(frame, (720, 480))
        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)

        # print(bbox)

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            # p1 = (int(bbox[0] + (bbox[2] / 2)), int(bbox[1] + (bbox[3] / 2)))
            cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)
            # cv2.circle(frame, p1, int(bbox[3]/2), (0, 0, 255), 2, 0)
        else:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display tracker type on frame
        cv2.putText(frame, tracker_type + " Tracker", (50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display FPS on frame
        cv2.putText(frame, "FPS : " + str(int(fps)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        cv2.putText(frame, "Center : (" + str(int(bbox[0])) + ',' + str(int(bbox[1])) + ")", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        cv2.putText(frame, "Size : " + str(int(bbox[2] * bbox[3])), (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (0, 0, 255), 2)

        out.write(frame)

        # Display result
        cv2.imshow("Tracking", frame)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27: break
