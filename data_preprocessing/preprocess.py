import os
import music21 as m21
import json
import keras as keras
import tensorflow as tf
import numpy as np

KERN_DATASET_PATH = "deutschl/test" # path to the dataset
SINGLE_FILE_DATASET = "dataset" # text files of encoded songs
OUTPUT_DIR = "output_musicxml" # for manually testing xml files
MAPPINGS_PATH = "mappings.json" # mappings file
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
        save_path = os.path.join(SINGLE_FILE_DATASET, f"song_{i}.txt")
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
    for song in songs:
        int_song = [mappings[symbol] for symbol in song.split()]
        int_songs.append(int_song)
    return int_songs

def generate_training_sequences(sequence_length):
    # load songs and map them to int
    songs = open("dataset.txt", "r").read()
    int_songs = convert_songs_to_int(songs)
    
    # generate the sequences
    network_input = []
    network_output = []
    for i in range(len(int_songs) - sequence_length):
        network_input.append(int_songs[i:i+sequence_length])
        network_output.append(int_songs[i+sequence_length])
    # one hot encode the sequences
    vocabulary_size = len(set(songs))
    network_input = keras.utils.to_categorical(network_input, num_classes=vocabulary_size)
    network_output = np.array(network_output)
    return network_input, network_output


if __name__ == "__main__":
    preprocess(KERN_DATASET_PATH, OUTPUT_DIR)
    
    songs = merge_dataset_to_file(SINGLE_FILE_DATASET, "dataset.txt")
    
    create_mapping(songs, MAPPINGS_PATH)
    
    inputs, outputs = generate_training_sequences(SEQUENCE_LENGTH)
    
