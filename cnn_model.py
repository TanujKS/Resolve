from keras.models import Sequential
from keras import layers
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from keras.backend import clear_session
import numpy as np
clear_session()

df = pd.read_json("reddit_data/data.json")

df_reddit = df[['title', 'sig_scores']]
posts = df_reddit['title'].to_list()
y_values = df_reddit['sig_scores'].to_list()

print(df_reddit.head())
print(df_reddit.tail())

x_train, x_test, y_train, y_test = train_test_split(posts, y_values, test_size=0.25, random_state=1000)

vectorizer = CountVectorizer()
vectorizer.fit(x_train)

x_train = vectorizer.transform(x_train)
x_test = vectorizer.transform(x_test)

input_dim = x_train.shape[1]
print(input_dim)


model = Sequential()
model.add(layers.Dense(10, input_dim=input_dim, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(
    loss='binary_crossentropy',
    optimizer='adam',
    metrics=['accuracy'])

model.summary()

history = model.fit(x_train, np.array(y_train), epochs=100, verbose=False, validation_data=(x_test, y_test), batch_size=10)

loss, accuracy = model.evaluate(x_train, y_train, verbose=False)
print("Training Accuracy: {:.4f}".format(accuracy))
loss, accuracy = model.evaluate(x_test, y_test, verbose=False)
print("Testing Accuracy:  {:.4f}".format(accuracy))
