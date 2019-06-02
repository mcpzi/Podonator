import cv2
img=cv2.imread("Calibration\\patternLR.jpg")
img2=cv2.rotate(img,rotateCode=cv2.ROTATE_90_CLOCKWISE)
cv2.imshow('Original', img)
cv2.imshow('Rotation', img2)
cv2.waitKey(0)
