import music21 as m21

def load_songs(data_path):
    #go through all files in data set and load them with music21
    for path, subdir, files in os.walk(data_path):
        for file in files:
            if file.endswith(".krn"):
                song = converter.parse(os.path.join(path, file))
                songs.append(song)
    




def preprocess(data_path):
    pass
    #load songs
    
    #filter out songs with non-acceptable duration
    
    #transpose to C major
    
    #encode songs with music time series representation
    
    #save songs to text file