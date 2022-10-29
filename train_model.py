import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

df = pd.read_json("reddit_data/data.json")

df_reddit = df[['title', 'sig_scores']]
posts = df_reddit['title'].to_list()
y_values = df_reddit['sig_scores'].to_list()

print(df_reddit.head())
print(df_reddit.tail())

post_train, post_test, y_train, y_test = train_test_split(posts, y_values, test_size=0.25, random_state=1000)

vectorizer = CountVectorizer()
vectorizer.fit(post_train)

x_train = vectorizer.transform(post_train)
x_test = vectorizer.transform(post_test)



classifier = LogisticRegression()
classifier.fit(x_train, y_train)
score = classifier.score(x_test, y_test)

print("Accuracy:", score)

x_test = vectorizer.transform(["To establish a post office"])
#
y_pred = classifier.predict(x_test)
#
print(y_pred)
