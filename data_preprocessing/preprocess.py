import os
import music21 as m21

KERN_DATASET_PATH = "deutschl/test"

def load_songs(data_path):
    songs = []
    # Go through all files in the dataset and load them with music21
    for path, subdirs, files in os.walk(data_path):
        for file in files:
            if file.endswith(".krn"):
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs

def preprocess(data_path, output_dir):
    # Load songs
    print("Loading songs...")
    songs = load_songs(data_path)
    print(f"Loaded {len(songs)} songs.")
    
    # Save songs as MusicXML files
    for i, song in enumerate(songs):
        output_file = os.path.join(output_dir, f"song_{i}.xml")
        song.write('xml', output_file)

    print(f"MusicXML files saved to {output_dir}")

if __name__ == "__main__":
    OUTPUT_DIR = "output_musicxml"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Starting preprocessing...")
    preprocess(KERN_DATASET_PATH, OUTPUT_DIR)
