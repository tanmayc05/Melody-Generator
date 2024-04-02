import os
import music21 as m21

KERN_DATASET_PATH = "deutschl/test" # path to the dataset
SAVE_DIR = "dataset" # text files of encoded songs
OUTPUT_DIR = "output_musicxml" # for manually testing xml files
ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4] # in quarter length
SEQUENCE_LENGTH = 64
 
def load_songs(data_path):
    songs = []
    # Go through all files in the dataset and load them with music21
    for path, subdirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".krn"):
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

def has_acceptable_durations(song, acceptable_durations):
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def transpose(song):
    # Get key from the song
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measures_part0[0][4]  # assuming the key signature is the 5th element of the first measure
    # Estimate key using music21
    key = song.analyze("key")
    # Get interval for transposition. E.g., Bmaj -> Cmaj
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == "minor":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    # Transpose song by calculated interval
    transposed_song = song.transpose(interval)
    return transposed_song

def encode_song(song, time_step=0.25):
    # Convert song into string of characters
    encoded_song = []
    for event in song.flat.notesAndRests:
        # If it's a note
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi
        # If it's a rest
        elif isinstance(event, m21.note.Rest):
            symbol = "R"
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song


def preprocess(data_path, output_dir):
    # Load songs
    print("Loading songs...")
    songs = load_songs(data_path)
    print(f"Loaded {len(songs)} songs.")
    
    for i, song in enumerate(songs):
        # Filter out songs that have non-acceptable durations
        if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
            continue
        
        # Transpose songs to Cmaj/Amin
        song = transpose(song)
        
        # Encode songs with music21
        encoded_song = encode_song(song)
        
        # Save songs to text file
        save_path = os.path.join(SAVE_DIR, f"song_{i}.txt")
        with open(save_path, "w") as file:
            file.write(encoded_song)
        
        # Save songs to text file
        output_file = os.path.join(output_dir, f"song_{i}.xml")
        song.write('xml', output_file)
            
def merge_dataset_to_file(dataset_path, file_path):
    # Merge all songs into a single file
    new_song_delimiter = "/ " * SEQUENCE_LENGTH
    songs = ""
    for path, subdirs, files in os.walk(dataset_path):
        for file in files:
            with open(os.path.join(path, file), "r") as f:
                song = f.read()
                songs += song + " " + new_song_delimiter
    songs = songs[:-1]
    
    with open(file_path, "w") as file:
        file.write(songs)
    return songs
if __name__ == "__main__":
    print("Starting preprocessing...")
    preprocess(KERN_DATASET_PATH, OUTPUT_DIR)
    
