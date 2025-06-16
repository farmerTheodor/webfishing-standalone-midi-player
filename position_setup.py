from pynput import mouse, keyboard

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
        if string >= 4:
            current_note -= 1  # Adjust for the 5th and 6th string
            
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

            



if __name__ == "__main__":
    print(get_note_coordinates())
    
    