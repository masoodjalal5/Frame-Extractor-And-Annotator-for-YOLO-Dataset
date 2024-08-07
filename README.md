# Frame-Extractor-And-Annotator-for-YOLO-Dataset
Extracts frames from videos, allows an interface to draw bounding boxes and it outputs a text file with annotations for YOLO dataset


### This project is desinged to help create a custom dataset for a personal project

## Prerequisite
- OpenCV   version 4.10.0.84
- Numpy    version 1.21.6

### How to install
### Install OpenCv
```
pip install opencv-python==4.10.0.84
```
### Install Numpy
```
pip install numpy==1.21.6
```

if you find any issues while installation, please seek out support from relevant platforms (Documentation, StackOverflow, GPTs)

## How it works
The tool first reads a video file and picks frames at a specified rate. It uses OpenCV library to check for blurry images, the default threshold is 100, adjust it according to your needs. It then selects images that pass the blur threshold.

Afterwards, the images are opened in a window for manual annotation. Where the user must draw a bounding box around an object manually. There are hotkeys to assist in the process.

## Hot Keys

- Key 't'     : Rotates the bounding box 15 degrees anti-clockwise
- Key 'y'     : Rotates the bounding box 5 degrees anti-clockwise
- Key 'u'     : Rotates the bounding box 1 degrees anti-clockwise

- Key 'p'     : Rotates the bounding box 15 degrees clockwise
- Key 'o'     : Rotates the bounding box 5 degrees clockwise
- Key 'i'     : Rotates the bounding box 1 degrees clockwise

- Key 'd'     : Increases the length of bounding box by 4 pixels
- Key 'a'     : Decreases the length of bounding box by 4 pixels

- Key 'w'     : Increases the height of bounding box by 4 pixels
- Key 's'     : Decreases the height of bounding box by 4 pixels

- Up Button   :   moves the bounding box up by 2 pixels
- Down Button :   moves the bounding box down by 2 pixels
- Left Button :   moves the bounding box left by 2 pixels
- Right Button:   moves the bounding box right by 2 pixels

- Key 'k'     : Skips the frame, if deemed unnecessary or blurry on visual inspection
- Key 'j'     : Saves the frame along with annotation data

- Key 'x'     : Terminates the current video and loads the next video frames
- Key 'z'     : Terminates the program completely


The video/videos must be stored in the following folder
- path = "/videos"

- Next image will load when key 'k' is pressed, the image is skipped
- Next image will load when key 's' is pressed, the image and data are saved

- Next images will kepp loading until you run out of images, or press key 'x' to terminate the program.

## Folder Structure
The saved frames are stored in the following format
- Original Image              :   path = "/original_frames"
- Image with bounding box     :   path = "/output_frames"
- Image Annotation Labels     :   path = "/labels"

- The video/videos must be stored in the following folder
- path = "/videos"


## Attention
Images will keep loading until you run out of images, or press key 'x' to terminate the program.

## TODO
Implement functionality to read all the videos in the directory

## Disclosure
The project has been designed with the help of chatGPT. Why do the hardwork when there are tools to help you. You just need clear understanding of what you want and how you want it. Be prepared to troubleshoot issues yourself as chatGPT made a lot of logical errors during the process which required manual intervension.
