from flask import Flask, render_template, request
import numpy as np
import pandas as pd

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import re

app = Flask(__name__)

# dataset coronavirus WHO
pd.set_option('max_colwidth', 100)
data = pd.read_excel("WHO_FAQ.xlsx")

def preprocess_sentences(input_sentences):
    return [re.sub(r'(covid-19|covid)', 'coronavirus', str(input_sentence), flags=re.I) 
            for input_sentence in input_sentences]
        
# Load module containing USE
module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3')

# Creating response encodings
response_encodings = module.signatures['response_encoder'](
        input=tf.constant(preprocess_sentences(data.Answer)),
        context=tf.constant(preprocess_sentences(data.Context)))['outputs']

@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    userText = userText.split()
    userText = [''.join(userText)]

    # Creating encoding for user question
    question_encodings = module.signatures['question_encoder'](tf.constant(preprocess_sentences(userText)))['outputs']

    # Getting response
    test_responses = data.Answer[np.argmax(np.inner(question_encodings, response_encodings), axis=1)].values
    # test_responses.to_string()[4:].lstrip()
    return (str(test_responses)[2:-2])


if __name__ == "__main__":
    app.run()