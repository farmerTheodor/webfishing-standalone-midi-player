from time import sleep
import mido
import pydirectinput

from position_setup import get_note_coordinates
from window_manager import is_webfishing_actively_being_played 

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
    notes_to_play = figure_out_notes_to_play(list_of_notes)
    set_note_locations(notes_to_play)
    #play_strings(notes_to_play)



def figure_out_notes_to_play(list_of_notes):
    sorted_list_of_notes = sorted(list_of_notes)
    list_string_fret_pairs = []
    availables_strings = BUTTON_LOCATIONS.keys()
    
    for note in sorted_list_of_notes:
        usable_strings = NOTES_TO_STRING[note]
        availables_strings = list(set(availables_strings) & set(usable_strings))
        if len(availables_strings) == 0:
            break
        list_string_fret_pairs.append((availables_strings[0], note))
        availables_strings.pop(0)
        
    return list_string_fret_pairs


def set_note_locations(notes_to_play):
    for string, note in notes_to_play:
        x,y = BUTTON_LOCATIONS[string][note]
        pydirectinput.mouseDown(x, y)
        pydirectinput.mouseUp(x, y)
    
    
    
                
            
def play_strings(list_of_notes):
    num_to_key_mapping = {
        0: "q",
        1: "w",
        2: "e",
        3: "r",
        4: "t",
        5: "y",
    }
    keys_to_press = []
    
    for i in range(6):
        keys_to_press.append(num_to_key_mapping[i])
    
    for key in keys_to_press:
        pydirectinput.keyDown(key, _pause=False)
    
    for key in keys_to_press:
        pydirectinput.keyUp(key, _pause=False)
    
            
            


if __name__ == "__main__":
    main()