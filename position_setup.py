from time import sleep
import mss
import numpy as np
import cv2
from pynput import mouse, keyboard
from window_manager import is_webfishing_actively_being_played


def get_note_coordinates(starting_note=40):
    NUM_FRETS = 16
    NUM_STRINGS = 6
    
    strings = {}
    bounding_box = find_guitar()
    x, y, w, h = bounding_box
    string_spacing = w / NUM_STRINGS
    fret_spacing = h / NUM_FRETS
    for string in range(NUM_STRINGS):
        strings[string] = {}
        current_note = starting_note + 5 * string
        for fret in range(NUM_FRETS):
            x_coord = int(x + string_spacing/2 + string_spacing * string)
            y_coord = int(y+ fret_spacing/2 + fret_spacing * fret)
            strings[string][current_note] = (x_coord, y_coord)
            current_note += 1
    
    return strings

held_keys = {'ctrl': False, 'shift': False}
coordinates = []

def on_click(x, y, button, pressed):
    if pressed:
        if all(held_keys[key] for key in ('ctrl', 'shift')):
            coordinates.append((x, y))
            print(f"Captured coordinate: {x}, {y}")

            if len(coordinates) == 2:
                print(f"Final Coordinates: {coordinates}")
                return False  # Stop the listener

def on_press(key):
    try:
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            held_keys['ctrl'] = True
        if key in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]:
            held_keys['shift'] = True
    except AttributeError:
        pass

def on_release(key):
    try:
        if key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            held_keys['ctrl'] = False
        if key in [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r]:
            held_keys['shift'] = False
    except AttributeError:
        pass


def find_guitar():
    key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    key_listener.start()
    with mouse.Listener(on_click=on_click) as mouse_listener:
        mouse_listener.join()
    key_listener.stop()    
    

    sorted_coordinates = sorted(coordinates)
    x = sorted_coordinates[0][0]
    y = sorted_coordinates[0][1]
    w = sorted_coordinates[1][0] - sorted_coordinates[0][0]
    h = sorted_coordinates[1][1] - sorted_coordinates[0][1]
    
    return (x,y,w,h)
        
    # while True:
    #     image, bounding_box = _find_button("./button_images/guitar_interface.png")
    #     x,y,w,h = bounding_box
    #     if w > 50 and h > 30:
    #         return image, bounding_box
            


def _find_button(template_path):
    button_image_bounding_box = (None, (0,0,0,0))
    template_image = cv2.imread(template_path, cv2.IMREAD_COLOR)
    
    potential_candidates = []
    for i in range(5):
        screenshot = _capture_screen()
        unchecked_bounding_box = _find_button_once(template_image, screenshot)
        if unchecked_bounding_box is None:
            continue
        button_screenshot = screenshot[unchecked_bounding_box[1]:unchecked_bounding_box[1] + unchecked_bounding_box[3], unchecked_bounding_box[0]:unchecked_bounding_box[0] + unchecked_bounding_box[2]]
        
        if unchecked_bounding_box and button_screenshot.size > 0:
            potential_candidates.append((button_screenshot, unchecked_bounding_box))
    
    if potential_candidates:
        button_image_bounding_box = _find_best_candidate(potential_candidates,template_image)
    
    if button_image_bounding_box:
        x, y, w, h = button_image_bounding_box[1]
        screenshot = _capture_screen()
        cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Detected Button", screenshot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return button_image_bounding_box

def _capture_screen():
    while not is_webfishing_actively_being_played():
            print("Waiting for Webfishing to be active...")
            sleep(1)
            
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[1])  # Change the monitor index if needed
        img = np.array(screen)  # Convert to NumPy array for OpenCV processing
        return img

def _find_best_candidate(potential_candidates, template):
    best_match = None
    best_score = float('inf')  # Lower score is better in SSIM
    template_height, template_width = template.shape[:2]
    
    for candidate_img, bounding_box in potential_candidates:
        resized_candidate = cv2.resize(candidate_img, (template_width, template_height))
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        candidate_gray = cv2.cvtColor(resized_candidate, cv2.COLOR_BGR2GRAY)

        score = _compute_mean_squared_index(template_gray, candidate_gray)

        if score < best_score:
            best_score = score
            best_match = (candidate_img, bounding_box)

    return best_match

def _compute_mean_squared_index(imageA, imageB):
    """Compute the Mean Squared Error between two images."""
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err


def _find_button_once(template, screenshot):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()

    # Detect keypoints and descriptors
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(screenshot, None)

    # Use FLANN-based matcher for efficiency
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Match descriptors
    matches = flann.knnMatch(des1, des2, k=2)

    # Apply Lowe's ratio test
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:  # Threshold to filter good matches
            good_matches.append(m)

    # Proceed only if enough good matches are found
    MIN_MATCH_COUNT = 8
    if len(good_matches) >= MIN_MATCH_COUNT:
        # Extract matched keypoints
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Compute homography
        matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if matrix is None:
            return None
        
        # Get template dimensions
        h, w, _ = template.shape

        # Map the template’s bounding box to the screenshot
        pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, matrix)

        # Get bounding box coordinates
        x, y, w, h = cv2.boundingRect(dst)

        return (x, y, w, h)  # Return bounding box coordinates

    else:
        print("Not enough matches found.")
        return None



if __name__ == "__main__":
    print(get_note_coordinates())
    
    