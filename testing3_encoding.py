from imutils import paths
import face_recognition, pickle, cv2, os

uni_images="K:\\Coding\\python\\review2\\uploaded_files\\images"

def go():
    imagePaths = os.listdir(uni_images)
    knownEncodings = []
    knownNames = []

    for (i, imagePath) in enumerate(imagePaths):
        name = imagePath.split(os.path.sep)[-1]

        imagePath = uni_images +'\\'+ imagePath
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb,model='hog')

        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    data = {"encodings": knownEncodings, "names": knownNames}

    print('Now encodings were refreshed')
    f = open("face_enc", "wb")
    f.write(pickle.dumps(data))
    f.close()
