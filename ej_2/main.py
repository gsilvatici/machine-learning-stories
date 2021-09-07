import math
import numpy as np
import operator
import pandas as pd
import matplotlib.pyplot as plt


class Category:

    def __init__(self, name):
        self.name = name
        self.headline_count = 0
        self.words = {}
        self.relative_frequencies = {}

    def add_words_from_headline(self, headline):
        
        self.headline_count += 1

        keys = headline.lower().split()
        key_set = list(set(keys))

        for key in key_set:
        	# processed[key] = keys.count(key)
        	if key not in self.words.keys():
	            self.words[key] = 0
	        self.words[key] = self.words.get(key) + keys.count(key)  


    def learn(self):
	    # probability of each word
	    for word, cardinal in self.words.items():
	    	self.relative_frequencies[word] = (cardinal + 1) / (sum(self.words.values()) + 1)


class Bayes:

    def __init__(self, df):
        self.categories = {}
        for headline, category in zip(df['titular'], df['categoria']):
	        if category not in self.categories.keys():
	            self.categories[category] = Category(category)
	        self.categories[category].add_words_from_headline(headline)


    def learn(self, total_headlines):
    	for category in self.categories.values():
    		category.learn(total_headlines)
    	print("Bayes learning finished.")


def split_dataframe(df, percentage = 0.8):

    msk = np.random.rand(len(df)) < percentage
    training_data = df[msk]
    testing_data = df[~msk]

    return training_data, testing_data


news_data = pd.read_excel('Noticias_argentinas.xlsx')

news_data = news_data.loc[news_data['categoria'].notnull()]

categories = [
    'Salud',
    'Deportes',
    'Economia',
    'Ciencia y Tecnologia',
    'Entretenimiento',
    'Nacional',
    'Internacional'
]
print(len(news_data.index))


news_data = news_data.loc[news_data['categoria'].isin(categories)]

print(len(news_data.index))

training_data, test = split_dataframe(news_data, percentage=0.99)

bayes = Bayes(training_data)

bayes.learn()