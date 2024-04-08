#import preprocessing functions
from preprocess import generate_training_sequences, SEQUENCE_LENGTH
import tensorflow as tf
from tensorflow import keras

OUTPUT_UNITS = 122
NUM_UNITS = [256]
LOSS = "sparse_categorical_crossentropy"
LEARNING_RATE = 0.001
EPOCHS = 5
BATCH_SIZE = 64
SAVED_MODEL_PATH = "models/model.h5"

def build_model(output_units=OUTPUT_UNITS, num_units=NUM_UNITS, loss=LOSS, learning_rate=LEARNING_RATE):
    # create model arch
    input = keras.layers.Input(shape=(None, output_units))
    x = keras.layers.LSTM(num_units[0])(input)
    x = keras.layers.Dropout(0.2)(x)
    output = keras.layers.Dense(output_units, activation="softmax")(x)
    model = keras.models.Model(input, output)

    # compile model
    model.compile(loss=loss, optimizer=keras.optimizers.Adam(learning_rate), metrics=["accuracy"])
    model.summary()
    return model

    

def train(output_units=OUTPUT_UNITS, num_units=NUM_UNITS, loss=LOSS, learning_rate=LEARNING_RATE):
    # generate the training sequences
    inputs, outputs = generate_training_sequences(SEQUENCE_LENGTH)
    
    # build the network
    model = build_model(output_units, num_units, loss, learning_rate)
    
    # train the model
    model.fit(inputs, outputs, epochs=EPOCHS, batch_size=BATCH_SIZE)
    
    # save the model
    model.save(SAVED_MODEL_PATH)
    
if __name__ == "__main__":
    train()