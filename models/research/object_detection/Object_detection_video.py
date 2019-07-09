######## Video Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 1/16/18
# Description: 
# This program uses a TensorFlow-trained classifier to perform object detection.
# It loads the classifier uses it to perform object detection on a video.
# It draws boxes and scores around the objects of interest in each frame
# of the video.

## Some of the code is copied from Google's example at
## https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb

## and some is copied from Dat Tran's example at
## https://github.com/datitran/object_detector_app/blob/master/object_detection_app.py

## but I changed it to make it more understandable to me.

# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import sys

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'inference_graph'
VIDEO_NAME = 'test1.mov'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')

# Path to video
PATH_TO_VIDEO = os.path.join(CWD_PATH,VIDEO_NAME)

# Number of classes the object detector can identify
NUM_CLASSES = 4

# Load the label map.
# Label maps map indices to category names, so that when our convolution
# network predicts `5`, we know that this corresponds to `king`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Open video file
video = cv2.VideoCapture(PATH_TO_VIDEO)
count=0
while(video.isOpened()):

    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    ret, frame = video.read()
    cv2.imwrite("frame%d.jpg" % count, frame)
    frame_expanded = np.expand_dims(frame, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw the results of the detection (aka 'visulaize the results')
    vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.60)

    from PIL import Image, ImageFilter
    im = Image.open('frame%d.jpg'%count)
    width, height = im.size
    #print(width, height)

    #width = video.get(3)  
    #height = video.get(4)
    #width=int(width)
    #height=int(height)

    #print(width, height)

    box = np.squeeze(boxes)

    for i in range(len(boxes)):
        ymin = (int(box[i,0]*height))
        xmin = (int(box[i,1]*width))
        ymax = (int(box[i,2]*height))
        xmax = (int(box[i,3]*width))
        #print(ymin,xmin,ymax,xmax)
    #print(boxes)

    #print(frame[10][10][0])

    #cropped_image = im.crop((xmin,ymin,xmax,ymax))
    cropped_image = frame[ymin:ymax,xmin:xmax].copy()
    cropped_image = Image.fromarray(cropped_image)
    blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(radius=20))
    im.paste(blurred_image,(xmin,ymin,xmax,ymax))

    #cropped_image = frame[xmin:ymin,xmax:ymax]
    #blurred_image = cv2.medianBlur(cropped_image,5)
    #print(blurred_image)
    #print(cropped_image)
    #cropped_image.show()
    
    #frame[10][10]=blurred_image[10][10]
    #for i in range(ymax-ymin):
     #   for j in range(xmax-xmin):
      #      frame[i+xmin][j+ymin=blurred_image[i][j]

    count += 1
    
    b, g, r = im.split()
    im = Image.merge("RGB", (r, g, b))
    
    im = np.array(im)
    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', im)
    #im.show()
    
    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        print(count)
        print(num)
        break

# Clean up
video.release()
cv2.destroyAllWindows()
