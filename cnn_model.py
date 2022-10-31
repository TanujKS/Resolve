from keras.models import Sequential
from keras import layers
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from keras.backend import clear_session
import numpy as np
from scipy.sparse import csr_matrix
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

clear_session()

df = pd.read_json("reddit_data/data.json")

df_reddit = df[['title', 'sig_scores']]
posts = df_reddit['title'].values
y_values = df_reddit['sig_scores'].values


post_train, post_test, y_train, y_test = train_test_split(posts, y_values, test_size=0.25, random_state=1000)

tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(post_train)

x_train = tokenizer.texts_to_sequences(post_train)
x_test = tokenizer.texts_to_sequences(post_test)

vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index
maxlen = 100
embedding_dim = 50

x_train = pad_sequences(x_train, padding='post', maxlen=maxlen)
x_test = pad_sequences(x_test, padding='post', maxlen=maxlen)

input_dim = x_train.shape[1]


model = Sequential()
model.add(layers.Embedding(input_dim=vocab_size,
                           output_dim=embedding_dim,
                           input_length=maxlen))
model.add(layers.GlobalMaxPool1D())
model.add(layers.Flatten())
model.add(layers.Dense(10, input_dim=input_dim, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy'])

model.summary()


history = model.fit(x_train, y_train, epochs=100, verbose=False, validation_data=(x_test, y_test), batch_size=10)

loss, accuracy = model.evaluate(x_train, y_train, verbose=False)
print("Training Accuracy: {:.4f}".format(accuracy))
loss, accuracy = model.evaluate(x_test, y_test, verbose=False)
print("Testing Accuracy:  {:.4f}".format(accuracy))


model.save("testmodel2")
