from PIL.ImageChops import offset
from cvzone.FaceDetectionModule import FaceDetector
import cv2
import cvzone
from time import time

classID = 0 # 0 is fake 1 is real
outputFolderPath = 'Dataset/DataCollect'
offsetPercentageW = 10
offsetPercentageH = 20
confidence = 0.8
camWidth,camHeight = 640,480
floatingPoint = 6
save = True
blurThreshold = 35 #More value more focus



# Initialize the webcam
# '2' means the third camera connected to the computer, usually 0 refers to the built-in webcam
cap = cv2.VideoCapture(0)
cap.set(3,camWidth)
cap.set(4,camHeight)
# Initialize the FaceDetector object
# minDetectionCon: Minimum detection confidence threshold
# modelSelection: 0 for short-range detection (2 meters), 1 for long-range detection (5 meters)
detector = FaceDetector(minDetectionCon=0.5, modelSelection=0)

# Run the loop to continually get frames from the webcam
while True:
    # Read the current frame from the webcam
    # success: Boolean, whether the frame was successfully grabbed
    # img: the captured frame
    success, img = cap.read()
    imgOut = img.copy()

    blurList = [] #True or False values indicating if faces are blur are not
    listInfo = [] # Normalized values and the class name for the label txt file

    # Detect faces in the image
    # img: Updated image
    # bboxs: List of bounding boxes around detected faces
    img, bboxs = detector.findFaces(img, draw=False)

    # Check if any face is detected
    if bboxs:
        # Loop through each bounding box
        for bbox in bboxs:
            # bbox contains 'id', 'bbox', 'score', 'center'

            # ---- Get Data  ---- #
            center = bbox["center"]
            x, y, w, h = bbox['bbox']
            score = int(bbox['score'][0] * 100)

            #Check Score
            if score > confidence:

                #Fail Safe
                if x < 0:x=0
                if y < 0:y=0
                if w < 0:w=0
                if h < 0:h=0



                # Finding Blurriness
                imgFace = img[y:y + h, x:x + w]
                blurValue = int(cv2.Laplacian(imgFace, cv2.CV_64F).var())
                if blurValue > blurThreshold:
                    blurList.append(True)
                else:
                    blurList.append(False)
                cv2.imshow("Face", imgFace)

                #Normalization
                ih,iw,_ = img.shape
                xc,yc = x+w/2,y+h/2

                xcn = round(xc/iw,floatingPoint)
                ycn = round(yc/ih,floatingPoint)

                wn = round(w/iw,floatingPoint)
                hn = round(h / iw, floatingPoint)

                #Fail Safe
                if xcn > 1:xcn=1
                if ycn > 1:ycn=1
                if wn > 1:wn=1
                if hn > 1:hn=1

                listInfo.append(f"{classID} {xcn} {ycn} {wn} {hn}\n")
                # ---- Draw Data  ---- #

                cvzone.putTextRect(imgOut, f'Score:{int(score)}% Blur: {blurValue}%', (x, y - 10),scale=1)
                cvzone.cornerRect(imgOut, (x, y, w, h))




        if save:
            if all(blurList) and blurList!=[]:
                timeNow = time()
                timeNow = str(timeNow).split('.')
                timeNow = timeNow[0] + timeNow[1]
                cv2.imwrite(f"{outputFolderPath}{timeNow}.jpg",img)

                #Saving Label txt file
                for info in listInfo:
                    f = open(f"{outputFolderPath}{timeNow}.txt", 'a')
                    f.write(f"{info}")
                    f.close()

    # Display the image in a window named 'Image'
    cv2.imshow("Image", imgOut)
    # Wait for 1 millisecond, and keep the window open
    cv2.waitKey(1)