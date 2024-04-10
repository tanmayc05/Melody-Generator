import os
import music21 as m21
import json
import keras as keras
import numpy as np

KERN_DATASET_PATH = "training_set_2/Trap/Cymatics - Alarm - 127 BPM G Min.mid" # path to the dataset
ALL_SONGS_DATASET = "encoded_songs_dataset" # text files of encoded songs
MAPPINGS_PATH = "mappings.json" # mappings file
ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4] # in quarter length
SEQUENCE_LENGTH = 64
 
def load_songs(data_path):
    songs = []
    # Go through all files in the dataset and load them with music21
    # # if u encounter a file called "individual chords" then dont load it
    # for path, subdirs, files in os.walk(data_path):
    #     if "Individual Chords" in subdirs:
    #         subdirs.remove("Individual Chords")
    #     for file in files:
    #         if file.endswith(".krn"):
    #             song = m21.converter.parse(os.path.join(path, file))
    #             songs.append(song)
    #         # accept midi files
    #         if file.endswith(".mid"):
    #             song = m21.converter.parse(os.path.join(path, file))
    #             songs.append(song)
    songs.append(m21.converter.parse('training_set_2/Trap/Cymatics - Alarm - 127 BPM G Min.mid'))
    print(songs)
    return songs

def has_acceptable_durations(song, acceptable_durations):
    # account for chords and notes
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

def transpose(song):
    # Get key from the song
    parts = song.getElementsByClass(m21.stream.Part)
    measures_part0 = parts[0].getElementsByClass(m21.stream.Measure)
    key = measures_part0[0][3]  # assuming the key signature is the 5th element of the first measure
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
        # If it's a chord
        else:
            symbol = ".".join(str(n) for n in event.normalOrder)
        # Append the encoded symbol
        steps = int(event.duration.quarterLength / time_step)
        for step in range(steps):
            if step == 0:
                encoded_song.append(symbol)
            else:
                encoded_song.append("_")
    encoded_song = " ".join(map(str, encoded_song))
    return encoded_song


def preprocess(data_path):
    # Load songs
    print("Loading songs...")
    songs = load_songs(data_path)
    print(f"Loaded {len(songs)} songs.")
    
    for i, song in enumerate(songs):
        # Filter out songs that have non-acceptable durations
        # if not has_acceptable_durations(song, ACCEPTABLE_DURATIONS):
        #     continue
        
        # Transpose songs to Cmaj/Amin
        song = transpose(song)
        
        # Encode songs with music21
        encoded_song = encode_song(song)
        print(encoded_song)
        
        # Save songs to text file
        save_path = os.path.join(ALL_SONGS_DATASET, f"song_{i}.txt")
        with open(save_path, "w") as file:
            file.write(encoded_song)
            
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

def create_mapping(songs, mappings_file):
    mappings = {}
    
    # Identify the vocabulary
    songs = songs.split()
    vocabulary = list(set(songs))
    
    # Create mappings
    for i, symbol in enumerate(vocabulary):
        mappings[symbol] = i
    
    # Save the mappings to a JSON file
    with open(mappings_file, "w") as file:
        json.dump(mappings, file, indent=4)

def convert_songs_to_int(songs):
    # Load mappings
    with open(MAPPINGS_PATH, "r") as file:
        mappings = json.load(file)
    
    # Convert songs to int
    int_songs = []
    
    songs = songs.split()
    for symbol in songs:
        int_songs.append(mappings[symbol])
        
    return int_songs

def generate_training_sequences(sequence_length):
    # load songs and map them to int
    songs = open("dataset.txt", "r").read()
    int_songs = convert_songs_to_int(songs)
    
    # generate the training sequences and account for chords
    inputs = []
    targets = []
    num_sequences = len(int_songs) - sequence_length
    for i in range(num_sequences):
        inputs.append(int_songs[i:i+sequence_length])
        targets.append(int_songs[i+sequence_length])
        
    # one-hot encode the sequences
    vocabulary_size = len(set(int_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes=vocabulary_size)
    targets = np.array(targets)
    
    return inputs, targets


if __name__ == "__main__":
    preprocess(KERN_DATASET_PATH) 
    
    songs = merge_dataset_to_file(ALL_SONGS_DATASET, "dataset.txt")
    
    create_mapping(songs, MAPPINGS_PATH)
    
    inputs, outputs = generate_training_sequences(SEQUENCE_LENGTH)
    
