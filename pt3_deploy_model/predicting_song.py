import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np 
from tensorflow import keras

def main():
	artist_=input("Name of the artist: ")
	artist_ = artist_.lower().replace(" ","")
	lang_=input("Select language (ES or EN): ")
	seed_t=input("Palabra de Inicio: ")
	tokenizer_ = Tokenizer()
	model_ = keras.models.load_model(f"../models/{lang_}/{artist_}/")
	corpus, total_w= creating_tokens(artist=artist_, lang=lang_, tokenizer=tokenizer_)
	max_len = creating_sequences(corpus=corpus, tokenizer=tokenizer_, total_words= total_w)
	write_song(seed_text=seed_t, next_words=15, tokenizer=tokenizer_, max_sequence_len=max_len, model=model_)


def creating_tokens(artist, lang, tokenizer):
	data = open(f'../lyrics/{lang}/{artist}.txt', encoding="utf-8").read()
	corpus = data.lower().split("\n")
	tokenizer.fit_on_texts(corpus)
	total_words = len(tokenizer.word_index) + 1
	print(total_words)
	return corpus, total_words

def creating_sequences(corpus, tokenizer, total_words):
	input_sequences = []
	for line in corpus:
		token_list = tokenizer.texts_to_sequences([line])[0]
		for i in range(1, len(token_list)):
			n_gram_sequence = token_list[:i+1]
			input_sequences.append(n_gram_sequence)

	# pad sequences 
	max_sequence_len = max([len(x) for x in input_sequences])
	input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

	return max_sequence_len

def write_song(seed_text, next_words, tokenizer, max_sequence_len, model):
	for _ in range(next_words):
		token_list = tokenizer.texts_to_sequences([seed_text])[0]
		token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
		predicted = np.argmax(model.predict(token_list, verbose=0), axis=-1)
		output_word = ""
		for word, index in tokenizer.word_index.items():
			if index == predicted:
				output_word = word
				break
		seed_text += " " + output_word
	print(seed_text)


if __name__ == "__main__":
    # execute only if run as a script
    main()
