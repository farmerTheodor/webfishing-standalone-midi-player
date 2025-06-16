from time import time
from time import sleep
import mido
import pydirectinput

from position_setup import get_note_coordinates
from window_manager import is_webfishing_actively_being_played

# Disable pydirectinput's built-in pauses
pydirectinput.PAUSE = 0
pydirectinput.MINIMUM_DURATION = 0.01  # Small duration to ensure keys register
pydirectinput.MINIMUM_SLEEP = 0 

class StringState:
    def __init__(self, string=-1, last_played=0):
        self.note = string
        self.last_played = last_played
        
    def __repr__(self):
        return f"StringState(note={self.note}, last_played={self.last_played})"

class NoStringsAvailable(Exception):
    pass

NOTE_COOLDOWN = .1
CURRENT_STATE = {
    0:StringState(),
    1:StringState(),
    2:StringState(),
    3:StringState(),
    4:StringState(),
    5:StringState(),
}

BUTTON_LOCATIONS = get_note_coordinates()
NOTES_TO_STRING = {}
for string in BUTTON_LOCATIONS:
    for note in BUTTON_LOCATIONS[string].keys():
        if note not in NOTES_TO_STRING:
            NOTES_TO_STRING[note] = []
        NOTES_TO_STRING[note].append(string)        

def main():
    with mido.open_input() as inport:
        print("Listening for MIDI input...")
        while True:
            list_of_notes = get_list_of_notes_to_play(inport)
            if is_webfishing_actively_being_played():
                play_notes(list_of_notes)                
                
                
def get_list_of_notes_to_play(inport):
    list_of_notes = []
    for msg in inport.iter_pending():
        if msg.type == "note_on":
            list_of_notes.append(msg.note)
    return list_of_notes


def play_notes(list_of_notes):
    if len(list_of_notes) == 0:
        return
        
    notes_to_play = []
    try:
        notes_to_play = figure_out_notes_to_play_with_cooldown(list_of_notes)
    except NoStringsAvailable:
        notes_to_play = figure_out_notes_to_play_forced(list_of_notes)
        
    set_note_locations(notes_to_play)
    play_strings(notes_to_play)



def figure_out_notes_to_play_with_cooldown(list_of_notes):
    sorted_list_of_notes = sorted(list_of_notes)
    list_string_fret_pairs = []
    current_time = time()
    availables_strings = [
        string_num for string_num in BUTTON_LOCATIONS.keys() 
        if current_time - CURRENT_STATE[string_num].last_played > NOTE_COOLDOWN
    ]
    if len(availables_strings) == 0: # if no strings are available after filtering by time
        raise NoStringsAvailable("No available strings to play any notes")
    
    for note in sorted_list_of_notes:
        if note not in NOTES_TO_STRING:
            continue            
        
        usable_strings = NOTES_TO_STRING[note]
        availables_strings = list(set(availables_strings) & set(usable_strings))
        if len(availables_strings) == 0:
            raise NoStringsAvailable("No available strings to play the note")
        list_string_fret_pairs.append((availables_strings[0], note))
        availables_strings.pop(0)
        
    return list_string_fret_pairs


def figure_out_notes_to_play_forced(list_of_notes):
    sorted_list_of_notes = sorted(list_of_notes)
    list_string_fret_pairs = []
    availables_strings = BUTTON_LOCATIONS.keys()
    
    for note in sorted_list_of_notes:
        if note not in NOTES_TO_STRING:
            continue
        
        usable_strings = NOTES_TO_STRING[note]
        availables_strings = list(set(availables_strings) & set(usable_strings))
        if len(availables_strings) == 0:
            break
        list_string_fret_pairs.append((availables_strings[0], note))
        availables_strings.pop(0)
        
    return list_string_fret_pairs


def set_note_locations(notes_to_play):
    new_state = {}
    mouse_positions = []
    # Get Mouse positions
    for string, note in notes_to_play:
        if _is_note_location_already_set(string, note):
            continue       
        new_state[string] = note
        x, y = BUTTON_LOCATIONS[string][note]
        mouse_positions.append((x, y))
    
    # Click on the positions
    for x, y in mouse_positions:
        pydirectinput.click(x, y, _pause=False)
    
    # Update the current state of fingers on the guitar strings
    for string_state in new_state.keys():
        CURRENT_STATE[string_state].note = new_state[string_state]

def _is_note_location_already_set(string, note):
    return CURRENT_STATE[string].note == note
    
    
    
                
            
def play_strings(list_of_notes):
    print("Playing strings:", list_of_notes)
    num_to_key_mapping = {
        0: "q",
        1: "w",
        2: "e",
        3: "r",
        4: "t",
        5: "y",
    }
    keys_to_press = []
    
    for note in list_of_notes:
        string_to_play, _ = note
        keys_to_press.append(num_to_key_mapping[string_to_play])
    
    for key in keys_to_press:
        pydirectinput.keyDown(key, _pause=False)
    # Small delay to ensure the game registers the key presses
    sleep(0.05)
    for key in keys_to_press:
        pydirectinput.keyUp(key, _pause=False)
        
    for note in list_of_notes:
        string, _ = note
        CURRENT_STATE[string].last_played = time()
        
    
            
            


if __name__ == "__main__":
    main()