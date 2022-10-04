import os
import cv2, base64, numpy as np
from pyzbar.pyzbar import decode

# Make one method to decode the barcode
temp_path="K:\\Coding\\python\\review2\\fakebar.jpeg"
def BarcodeReader(image):

	img_binary = base64.b64decode(image)

	img_jpg = np.frombuffer(img_binary, dtype=np.uint8)

	img = cv2.imdecode(img_jpg, cv2.IMREAD_COLOR)
	cv2.imwrite(temp_path, img)

	img1 = cv2.imread(temp_path)
	id=''
	detectedBarcodes = decode(img1)
	print(detectedBarcodes)
	if not detectedBarcodes:
		print("Barcode Not Detected or your barcode is blank/corrupted!")
	else:
		for barcode in detectedBarcodes:
			(x, y, w, h) = barcode.rect
			cv2.rectangle(img1, (x-10, y-10),
						(x + w+10, y + h+10),
						(255, 0, 0), 2)
			if barcode.data!="":
				id = barcode.data.decode('utf-8')

	os.remove(temp_path)
	return id



# image = "K:\\Coding\\python\\kFlask\\bar.jpg"
# BarcodeReader(image)

