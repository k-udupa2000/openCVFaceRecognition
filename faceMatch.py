import numpy as np
import cv2
import os
import time
import speech_recognition as s_r
import cv2
from gtts import gTTS
import face_recognition
import serial

# Port connecting to arduino.
ArduinoUnoSerial = serial.Serial('/dev/ttyACM0',9600)
ArduinoUnoSerial.write('0')
def speakOut(message, name):
    # Text to mp3 converter.
    if(name != "default"):
        tts = gTTS(text=message + name, lang='en', slow = False)
    else:
        tts = gTTS(text=message, lang='en', slow = False)

    fileName = name + ".mp3"
    tts.save(fileName)

    # Playing mp3 file.
    from pygame import mixer
    mixer.init()
    mixer.music.load(fileName)
    mixer.music.play()
    time.sleep(6)
    # mp3 file removed.
    os.remove(fileName)

def microPhoneInput():
    r = s_r.Recognizer()
    with s_r.Microphone() as source:
        print("Say now!!")
        audio = r.listen(source)
        print("You said " + r.recognize_google(audio))
        name  = r.recognize_google(audio)
        # This will the name of the file.
        #print(r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY"))
        time.sleep(1)
        os.rename("./newFile.jpeg", "./StoredImages/" + name + ".jpeg")
        speakOut("New image has been registered with the name ", name)

if __name__ == "__main__":
    face_cascade = cv2.CascadeClassifier('data/haarcascade_frontalface_alt2.xml')
    cap = cv2.VideoCapture(0)
    flag = 0
    count = 0
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors=5)
        # Display the resulting frame
        cv2.imshow('frame',frame)
        if len(faces) > 0:
            #path = './StoredImages'
            for (x, y, w, h) in faces:
                    roi_color = frame[y: y + h, x : x + w]
                    cv2.imwrite("newFile.jpeg", roi_color)
            for filename in os.listdir("/home/karthik_udupa/opPro/newSeries/StoredImages"):
                if filename.endswith(".jpeg"):
                    try:
                        print(filename)
                        known_image = face_recognition.load_image_file("/home/karthik_udupa/opPro/newSeries/StoredImages/" + filename)
                        known_image_encoding = face_recognition.face_encodings(known_image)[0]

                        unknownImage = face_recognition.load_image_file("/home/karthik_udupa/opPro/newSeries/" + "newFile.jpeg")
                        unknownImage_encoding = face_recognition.face_encodings(unknownImage)[0]
                        results = face_recognition.compare_faces([known_image_encoding], unknownImage_encoding)
                        if results[0]:
                            print("Hurray matched with " + filename)
                            print(os.path.splitext(filename)[0])
                            speakOut("The person standing in front is", os.path.splitext(filename)[0])
                            flag = 1
                            ArduinoUnoSerial.write('1')
                            time.sleep(2)
                            break
                    except:
                        break
            if flag == 1:
                break
            count += 1
            print("Face not detected. Please try again from a different angle")
            time.sleep(1)
            if count > 1:
                print("New face")
                speakOut("speak out your name", "default")

                microPhoneInput()
                break

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    ArduinoUnoSerial.write('0')
    cap.release()
    cv2.destroyAllWindows()

