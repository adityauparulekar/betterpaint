import cv2

# Get the Haar cascade and make it usable
facePath = "haarcascade_frontalface_default.xml"
gestPath = "haarcascades/handGest.xml"
cPalmPath = "haarcascades/closedFrontalPalm.xml"
palmPath = "haarcascades/palm.xml"
fistPath = "haarcascades/fist.xml"
handPath = "haarcascades/handCascade2.xml"
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + facePath)
gestCascade = cv2.CascadeClassifier(gestPath)
cPalmCascade = cv2.CascadeClassifier(cPalmPath)
palmCascade = cv2.CascadeClassifier(palmPath)
fistCascade = cv2.CascadeClassifier(fistPath)
handCascade = cv2.CascadeClassifier(handPath)

# print(cv2.data.haarcascades)
# print("Detection time.")

# Capture a frame from the video
video_capture = cv2.VideoCapture(0)

for i in range(100000):
    # Capture frame-by-frameq
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Get the faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Get the gestures
    gests = gestCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )

    # Get the closed palms
    cPalms = cPalmCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )

    # Get the palms
    palms = palmCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=2,
        minSize=(30, 30)
    )

    # Get the fists
    fists = fistCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )

    # Get the hands
    hands = handCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30)
    )

    # Print how many of each type of feature there are in each frame
    # print("Frame " + str(i) + ": There are " + str(len(faces)) + " faces.")
    # print("Frame " + str(i) + ": There are " + str(len(gests)) + " gestures.")
    # print("Frame " + str(i) + ": There are " + str(len(cPalms)) + " closed frontal palms.")

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #print ("Face at (" + str(x) + ", " + str(y) + ")")

    # Draw a rectangle around the gestures
    # for (x, y, w, h) in gests:
    #     cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    #     #print ("Gesture at (" + str(x) + ", " + str(y) + ")")

    # Draw a rectangle around the closed palms
    for (x, y, w, h) in cPalms:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
       # print (" at (" + str(x) + ", " + str(y) + ")")

    # Draw a rectangle around the palms
    for (x, y, w, h) in palms:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)
       # print (" at (" + str(x) + ", " + str(y) + ")")

    # Draw a rectangle around the fists
    for (x, y, w, h) in fists:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
       # print (" at (" + str(x) + ", " + str(y) + ")")

    # Draw a rectangle around the hands
    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), 2)
       # print (" at (" + str(x) + ", " + str(y) + ")")

    # Display the resulting frame
    cv2.imshow('Video', cv2.flip(frame, 1))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
