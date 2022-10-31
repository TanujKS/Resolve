from tensorflow import keras
model = keras.models.load_model('testmodel')
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_json("reddit_data/data.json")

df_reddit = df[['title', 'sig_scores']]
posts = df_reddit['title'].values
y_values = df_reddit['sig_scores'].values

post_train, post_test, y_train, y_test = train_test_split(posts, y_values, test_size=0.25, random_state=1000)

tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(post_train)
def getRelevancy(sentence):
#    sentence = "To designate a post office in Pennsylvania"

    sentence_test = tokenizer.texts_to_sequences([sentence])

    sentence_test = pad_sequences(sentence_test, padding='post', maxlen=100)

    return model.predict(sentence_test)

print(getRelevancy("A concurrent resolution authorizing the use of the rotunda of the Capitol for a ceremony to present the statue of Harry S. Truman from the people of Missouri."))
