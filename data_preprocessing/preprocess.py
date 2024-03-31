import os
import music21 as m21
m21.configure.run()

KERN_DATASET_PATH = "deutschl/test"

def load_songs(data_path):
    
    songs = []
    
    #go through all files in data set and load them with music21
    for path, subdirs, files in os.walk(data_path):
        for file in files:
            if file[-3:] == "krn":
                song = m21.converter.parse(os.path.join(path, file))
                songs.append(song)
    return songs
                
    




def preprocess(data_path):
    pass
    #load songs
    print("Loading songs...")
    songs = load_songs(data_path)
    print(f"Loaded {len(songs)} songs.")
    
    
    #filter out songs with non-acceptable duration
    
    #transpose to C major
    
    #encode songs with music time series representation
    
    #save songs to text file
    
if __name__ == "__main__":
    songs = load_songs(KERN_DATASET_PATH)
    print(f'Loaded {len(songs)} songs.')
    song = songs[0]
    song.show()