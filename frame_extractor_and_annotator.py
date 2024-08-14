'''
Attention:

Frame Extractor and Annotator for YOLO Dataset

YOLO Dataset Maker is desinged to help create a custom dataset for personally projects

The tool first reads a video file and picks frames at a specified rate. It uses OpenCV library
to check for blurry images, the default threshold is 100, adjust it according to your needs.
It then selects images that pass the blur threshold.

Afterwards, the images are opened in a window for manual annotation.
Where the user must draw a bounding box around an object manually.
There are hotkeys to assist in the process.

key 't'     : Rotates the bounding box 15 degrees anti-clockwise
key 'y'     : Rotates the bounding box 5 degrees anti-clockwise
key 'u'     : Rotates the bounding box 1 degrees anti-clockwise

key 'p'     : Rotates the bounding box 15 degrees clockwise
key 'o'     : Rotates the bounding box 5 degrees clockwise
key 'i'     : Rotates the bounding box 1 degrees clockwise

Key 'd'     : Increases the length of bounding box by 4 pixels
Key 'a'     : Decreases the length of bounding box by 4 pixels

Key 'w'     : Increases the height of bounding box by 4 pixels
Key 's'     : Decreases the height of bounding box by 4 pixels

Up Button   :   moves the bounding box up by 2 pixels
Down Button :   moves the bounding box down by 2 pixels
Left Button :   moves the bounding box left by 2 pixels
Right Button:   moves the bounding box right by 2 pixels

Key 'k'     : Skips the frame, if deemed unnecessary or blurry on visual inspection
Key 'j'     : Saves the frame along with annotation data

Key 'x'     : Terminates the current video and loads the next video frames
Key 'z'     : Terminates the program completely

The saved frames are stored in the following format
Original Image              :   path = "/original_frames"
Image with bounding box     :   path = "/output_frames"
Image Annotation Labels     :   path = "/labels"

The video/videos must be stored in the following folder
path = "/videos"

Next image will load when key 'k' is pressed, the image is skipped
Next image will load when key 's' is pressed, the image and data are saved

Next images will kepp loading until you run out of images, or press key 'x' 
to terminate the program.

TODO: Implement functionality to read all the videos in the directory


'''
import cv2
import numpy as np
import os
import sys

# Set the image resolution
frame_width = 640
frame_height = 360

drawing = False  # True if the mouse is pressed
dragging = False  # True if the mouse is dragging the bounding box
ix, iy = -1, -1  # Initial positions
bounding_boxes = []  # List to store bounding box coordinates
current_frame = None  # Current frame being processed
original_frame = None  # Original frame before being processed.
rotation_angle = 0  # Angle of rotation for bounding boxes
selected_box_idx = -1  # Index of the selected bounding box for dragging

bb_len_change = 0       # Length of bounding box
bb_height_change = 0    # Height of bounding box

bb_move_horiz = 0       # Move the bounding box horizontally
bb_move_vert = 0        # Move the bounding box vertically

class_id = 0            # Class ID of object


def is_blurry(frame, threshold=100):
    """Determine if the frame is blurry based on the Laplacian variance."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, dragging, current_frame, bounding_boxes, rotation_angle, selected_box_idx

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(bounding_boxes) == 0:
            drawing = True
            ix, iy = x, y
        else:
            for idx, (x1, y1, x2, y2, angle) in enumerate(bounding_boxes):
                if is_point_in_rotated_rect(x, y, x1, y1, x2, y2, angle):
                    dragging = True
                    selected_box_idx = idx
                    ix, iy = x, y
                    break

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = current_frame.copy()
            draw_rotated_rectangle(img_copy, ix, iy, x, y, rotation_angle)
            display_angle(img_copy, rotation_angle)
            display_class_id(img_copy, class_id)
            cv2.imshow('frame', img_copy)
        elif dragging:
            if selected_box_idx != -1:
                dx, dy = x - ix, y - iy
                x1, y1, x2, y2, angle = bounding_boxes[selected_box_idx]
                bounding_boxes[selected_box_idx] = (x1 + dx, y1 + dy, x2 + dx, y2 + dy, angle)
                ix, iy = x, y
                redraw_frame()

    elif event == cv2.EVENT_LBUTTONUP:
        if drawing:
            drawing = False
            bounding_boxes.append((ix, iy, x, y, rotation_angle))
            draw_rotated_rectangle(current_frame, ix, iy, x, y, rotation_angle)
            display_angle(current_frame, rotation_angle)
            display_class_id(current_frame, class_id)
            cv2.imshow('frame', current_frame)
        elif dragging:
            dragging = False
            selected_box_idx = -1

def is_point_in_rotated_rect(px, py, x1, y1, x2, y2, angle):
    """Check if a point (px, py) is inside the rotated rectangle."""
    center = ((x1 + x2) / 2, (y1 + y2) / 2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    box = np.array([
        [-width / 2, -height / 2],
        [width / 2, -height / 2],
        [width / 2, height / 2],
        [-width / 2, height / 2]
    ])

    rotation_matrix = cv2.getRotationMatrix2D((0, 0), angle, 1)
    rotated_box = np.dot(rotation_matrix[:, :2], box.T).T + center

    poly = np.array(rotated_box, np.int32)
    return cv2.pointPolygonTest(poly, (px, py), False) >= 0

def draw_rotated_rectangle(img, x1, y1, x2, y2, angle):
    """Draw a rotated rectangle on the image."""
    center = ((x1 + x2) / 2, (y1 + y2) / 2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    box = np.array([
        [-width / 2, -height / 2],
        [width / 2, -height / 2],
        [width / 2, height / 2],
        [-width / 2, height / 2]
    ])

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)
    rotated_box = np.dot(rotation_matrix[:, :2], box.T).T + center

    rotated_box = np.int0(rotated_box)
    cv2.polylines(img, [rotated_box], isClosed=True, color=(0, 255, 0), thickness=2)

def display_angle(img, angle):
    """Display the angle on top of the frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f'Angle: {angle:.1f}'
    cv2.putText(img, text, (10, 30), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

def display_class_id(img, class_id):
    """Display the angle on top of the frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f'Class: {chr(class_id)}'
    cv2.putText(img, text, (250, 30), font, 1, (255, 255, 255), 1, cv2.LINE_AA)

def save_annotations(output_dir, frame_name, width, height):
    global rotation_angle, class_id
    annotation_path = os.path.join(output_dir, frame_name.replace('.jpg', '.txt'))
    with open(annotation_path, 'w') as f:
        for (x1, y1, x2, y2, angle) in bounding_boxes:
            # Convert to YOLO format: class x_center y_center width height angle
            x_center = (x1 + x2) / 2 / width
            y_center = (y1 + y2) / 2 / height
            bbox_width = (x2 - x1) / width
            bbox_height = (y2 - y1) / height
            f.write(f"{chr(class_id)} {x_center} {y_center} {bbox_width} {bbox_height}\n")            
            # f.write(f"{chr(class_id)} {x_center} {y_center} {bbox_width} {bbox_height} {rotation_angle}\n")

def process_video(video_path, frame_interval, blur_threshold):
    """Read a video, select frames at constant intervals, and skip blurry frames."""
    global current_frame, bounding_boxes
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indices = np.arange(0, frame_count, frame_interval)

    selected_frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Unable to read frame at index {idx}")
            continue

        if not is_blurry(frame, blur_threshold):
            selected_frames.append((idx, frame))
        else:
            video_path.replace("videos/", "")
            print(f"{video_path} : Skipped blurry frame at index {idx}")

    cap.release()
    return selected_frames

def resize_frame(frame):
    """Resize the frame to the specified width and height."""
    global frame_width, frame_height
    return cv2.resize(frame, (frame_width, frame_height))

def redraw_frame():
    """Redraw the frame with all bounding boxes."""
    global current_frame, original_frame, bounding_boxes
    global bb_len_change, bb_height_change, bb_move_horiz, bb_move_vert, class_id
    
    current_frame = original_frame.copy()
    for (x1, y1, x2, y2, angle) in bounding_boxes:
        # Move Left/Right, Up/Down, Increase/Decrease Lenght/Height
        draw_rotated_rectangle(current_frame, x1 + (bb_move_horiz/2) - (bb_len_change/2) , y1 + (bb_move_vert/2) - (bb_height_change/2), x2 + (bb_move_horiz/2) + (bb_len_change/2), y2 + (bb_move_vert/2) + (bb_height_change/2), rotation_angle)
                    
    display_angle(current_frame, rotation_angle)
    display_class_id(current_frame, class_id)
    cv2.imshow('frame', current_frame)

def save_frames(frames, output_dir, original_frame_out_dir, label_dir, video_name):
    """Save selected frames to the specified directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(label_dir):
        os.makedirs(label_dir)
    if not os.path.exists(original_frame_out_dir):
        os.makedirs(original_frame_out_dir)
    
    global frame_width, frame_height
    global current_frame, original_frame, bounding_boxes, rotation_angle
    global bb_len_change, bb_height_change, bb_move_horiz, bb_move_vert
    global class_id

    for idx, frame in frames:
    
        try:
            f = open("last_frame.txt", "r")
            last_frame = f.read()
            if idx < int(last_frame):
                continue
        except:
            print("Starting from frame 0 \n")
            
        frame_name = f"{video_name}_frame_{idx:04d}.jpg"
        output_path = os.path.join(output_dir, frame_name)
        original_frame_out_path = os.path.join(original_frame_out_dir, frame_name)
        label_path = os.path.join(label_dir, frame_name.replace('.jpg', '.txt'))

        current_frame = resize_frame(frame)  # Resize the frame here
        original_frame = resize_frame(frame) 
        bounding_boxes = []
        rotation_angle = 0  # Reset angle for each new image
        bb_len_change = 0   # Reset change in length for new image
        bb_height_change = 0  # Reset change in height for new image
        bb_move_horiz = 0   # Reset Horizontal Movement
        bb_move_vert = 0    # Reset Vertical Movement
        is_move_horiz = False  # Reset Horizontal Movement
        is_move_vert = False   # Reset Vertical Movement
        
        # class_id = 0            # Reset Class id for next frame

        while True:
            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('frame', frame_width, frame_height)  # Set the window size
            cv2.imshow('frame', current_frame)
            cv2.setMouseCallback('frame', draw_rectangle)
            # key = cv2.waitKey(1) & 0xFF
            key = cv2.waitKeyEx(0)
            
            redraw_frame()
            
            if key == ord('j'):  # Save the annotations and move to the next frame
                cv2.imwrite(output_path, current_frame)
                cv2.imwrite(original_frame_out_path, original_frame)
                print(f"Saved frame to {output_path}")
                height, width = current_frame.shape[:2]
                save_annotations(label_dir, frame_name, width, height)
                break
            elif key == ord('k'):  # Skip the current frame
                print(f"Skipped frame at index {idx}")
                break	
			
            # Rotate Clockwise
            elif key == ord('p'):  # Rotate bounding boxes by -15 degrees
                rotation_angle = (rotation_angle - 15) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation
                redraw_frame()
            elif key == ord('o'):  # Rotate bounding boxes by -5 degrees
                rotation_angle = (rotation_angle - 5) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation
                redraw_frame()
            elif key == ord('i'):  # Rotate bounding boxes by -1 degrees
                rotation_angle = (rotation_angle - 1) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation
                redraw_frame()
                
            # Rotate Anti-Clockwise
            elif key == ord('u'):  # Rotate bounding boxes by 1 degrees
                rotation_angle = (rotation_angle + 1) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation
                redraw_frame()
            elif key == ord('y'):  # Rotate bounding boxes by 5 degrees
                rotation_angle = (rotation_angle + 5) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation
                redraw_frame()                
            elif key == ord('t'):  # Rotate bounding boxes by 15 degrees
                rotation_angle = (rotation_angle + 15) % 360
                current_frame = resize_frame(frame)  # Reset the frame for rotation                
                redraw_frame()
            
            # Increase/Decrease length of bounding box
            elif key == ord('d'):
                bb_len_change = bb_len_change + 4
                redraw_frame()
            elif key == ord('a'):
                bb_len_change = bb_len_change - 4
                redraw_frame()
            
            # Increase/Decrease height of bounding box
            elif key == ord('w'):
                bb_height_change = bb_height_change + 4
                redraw_frame()
            elif key == ord('s'):
                bb_height_change = bb_height_change - 4
                redraw_frame()
            
            # Move the bounding box Left/Right
            elif key == 2424832:  # Left arrow key
                bb_move_horiz = bb_move_horiz - 4
                redraw_frame()
            elif key == 2555904:  # Right arrow key
                bb_move_horiz = bb_move_horiz + 4
                redraw_frame()
            
            # Move the bounding box Up/Down
            elif key == 2490368:  # Up arrow key
                bb_move_vert = bb_move_vert - 4
                redraw_frame()
            elif key == 2621440:  # Down arrow key
                bb_move_vert = bb_move_vert + 4
                redraw_frame()
                
            elif ord('0') <= key <= ord('9'):
                class_id = key
                redraw_frame()
                
            elif key == ord('x'):  # Quit the program
                cv2.destroyAllWindows()
                return
            elif key == ord('z'): 
                print(f"closing at frame {idx}")
                f = open("last_frame.txt", "w")
                f.write(str(idx))
                f.close()
                sys.exit(0)
                
        
        cv2.destroyAllWindows()

if __name__ == "__main__":

    # Output paths
    destination_path = "output_frames"
    label_path = "labels"
    original_frame_out_path = "original_frames"
    
    videos_list = []
    
    #video_path = "videos\\Blue Pointer 2.mp4"
    video_directory = "videos/"         # Define the directory containing the videos
    files = os.listdir(video_directory) # Get a list of all files in the directory

    # Filter out non-video files (you can extend this list with other video formats if needed)
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv')
    video_files = [f for f in files if f.lower().endswith(video_extensions)]
    
    try:
        f = open("video_completion_log.txt", "r")
        videos_list = f.readlines()
        videos_list = [line.strip() for line in videos_list]
    except:
        print("Running for the first time \n")
    
    # Loop through each video file and read it
    for video_file in video_files:
        
        video_path = os.path.join(video_directory, video_file)
        video_name = video_file.lower().replace(".mp4", "").replace(" ", "_").replace("-","_")
        
        # checks if videos_list is not empty or video name is in the list
        # This condition is only true if the list is not empty and the name is in the list
        # If it is true, then it means the video had been previously processed and skipped this time.        
        if videos_list and video_name in videos_list:
            print(f"Skipped: {video_name} \t\t Reason: video was processed previously ...")
            continue

        selected_frames = process_video(video_path, frame_interval=5, blur_threshold=100)
        save_frames(selected_frames, destination_path, original_frame_out_path, label_path, video_name)
        
        f = open("video_completion_log.txt", "a")
        f.write(video_name)
        f.write("\n")
        f.close()
        
        f = open("last_frame.txt", "w")
        f.write(str(0))
        f.close()
    
    print("\n.... All Done ....\n")
