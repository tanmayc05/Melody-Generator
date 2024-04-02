import os
import music21 as m21

KERN_DATASET_PATH = "deutschl/test"
ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4]
 
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
        
        # Save songs to text file
        output_file = os.path.join(output_dir, f"song_{i}.xml")
        song.write('xml', output_file)
            
        

if __name__ == "__main__":
    OUTPUT_DIR = "output_musicxml"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting preprocessing...")
    preprocess(KERN_DATASET_PATH, OUTPUT_DIR)
