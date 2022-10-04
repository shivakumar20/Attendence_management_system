from time import sleep
import face_recognition, pickle, cv2, testing3_encoding, base64, numpy as np, os

temp_path="K:\\Coding\\python\\review2\\fake.jpeg"
uni_images="K:\\Coding\\python\\review2\\uploaded_files\\images"
uni_encodings="K:\\Coding\\python\\review2\\face_enc"

def save_img(img_base64, id):
    img_binary = base64.b64decode(img_base64)

    img_jpg=np.frombuffer(img_binary, dtype=np.uint8)

    img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)

    # DETECTING FACE FOR TEMPORARY CHECK
    cv2.imwrite(temp_path, img)

    # THE REAL FUNCTION FOR COMPARING FACES
    flag = go(id + '.png')
    
    print(flag)
    if(flag == False):
        return "Not able to take the attendace"

    return flag

def go(id):
    # DISCLAIMER: FOR DETECTING ALL THE FACES IF NEW WERE ADDED AND STORING IT IN A FILE
    imagePaths = os.listdir(uni_images)
    print(imagePaths, 'imagepaths')

    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    data = pickle.loads(open(uni_encodings, "rb").read())

    # LIVE IMAGE OF A STUDENT
    image = cv2.imread(temp_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if len(data['names']) != len(imagePaths):
        print("Some new images were added, refreshing encoded data")
        sleep(3)
        testing3_encoding.go()
        data = pickle.loads(open(uni_encodings, "rb").read())

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray,
                                        scaleFactor=1.1,
                                        minNeighbors=5,
                                        minSize=(60, 60),
                                        flags=cv2.CASCADE_SCALE_IMAGE)

    names = []
    encodings = face_recognition.face_encodings(rgb)

    index = data['names'].index(id)

    os.remove(temp_path)
    if len(encodings) == 1:
        matches = face_recognition.compare_faces(data["encodings"][index], encodings)    
        if True in matches:
            print('found a match for you ')
            return id; #16 
        else:
            return 'Not able to find a match'; #24

    elif len(encodings) > 1:
        return 'More than one face has been detected'; #36
    else:
        return 'ERROR in detecting the face' #27


# for encoding in encodings:

#     matches = face_recognition.compare_faces(data["encodings"], encoding)
#     print(data["encodings"][index])
#     print('------------------')
#     print(encoding)

#     if True in matches:
#         matchedIdxs = [i for (i, b) in enumerate(matches) if b]
#         for i in matchedIdxs:
#             name = data["names"][i]
#         names.append(name)
#         print('found a match for you ', name)
#     else:
#         print('not able to find a match for you')