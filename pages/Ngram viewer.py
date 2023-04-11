"""
# Alan's toolbox

"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import re
import unidecode
import nltk
import io
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import ngrams
from bs4 import BeautifulSoup
from collections import Counter
from xlsxwriter import Workbook

#DEF
def remove_newlines_tabs(text):
    Formatted_text = text.replace('\\n', ' ').replace('\n', ' ').replace('\t',' ').replace('\\', ' ').replace('. com', '.com')
    return Formatted_text

def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    # Get all the text other than html tags.
    stripped_text = soup.get_text(separator=" ")
    return stripped_text

def remove_whitespace(text):
    pattern = re.compile(r'\s+') 
    Without_whitespace = re.sub(pattern, ' ', text)
    text = Without_whitespace.replace('?', ' ? ').replace(')', ') '.replace('!',' ! '))
    return text 

def accented_characters_removal(text):
    text = unidecode.unidecode(text)
    return text

def lower_casing_text(text):
    text = text.lower()
    return text

def removing_special_characters(text):
    Formatted_Text = re.sub(r"[^a-zA-Z0-9]+", ' ', text)
    #Formatted_Text = re.sub(r"[^a-zA-Z0-9:$-,%.?!]+", ' ', text)
    return Formatted_Text

def removing_stopwords(text,lang):
    #https://medium.com/analytics-vidhya/removing-stop-words-with-nltk-library-in-python-f33f53556cc1
    # Add text
    tokens = word_tokenize(text.lower())
    lang_stopwords = stopwords.words(lang)
    tokens_wo_stopwords = [t for t in tokens if t not in lang_stopwords]
    return " ".join(tokens_wo_stopwords)

def lemmatizer(text):
    tokens = word_tokenize(text)    
    lemmatizer = WordNetLemmatizer()    
    lemmatized_words = [lemmatizer.lemmatize(token) for token in tokens]    
    lemmatized_text = ' '.join(lemmatized_words)    
    return lemmatized_text


#HEADER
st.set_page_config(layout="wide")
st.title("Ngram Viewer ")

#BODY
st.header("Input")
txt = st.text_area(label="Text to be analyzed :",height=400)

st.header("Preprocess")
newlines_tabs = st.checkbox('Remove newlines tabs',value=True)
remove_html = st.checkbox('Strip html tags',value=True)
extra_whitespace = st.checkbox('Remove extra whitespaces',value=True)
accented_chars = st.checkbox('Replace accented characters',value=True)
lowercase = st.checkbox('Lower casing',value=True)
punctuations = st.checkbox('Remove punctuations',value=True)
remove_stopwords = st.checkbox('Remove stopwords',value=False)
lemm = st.checkbox('Lemmatize',value=False)

if remove_stopwords :
    st.header("Stopwords")
    lang = st.selectbox('Choose a language :', ["arabic","azerbaijani","basque","bengali","catalan","chinese","danish","dutch","english","finnish","french","german","greek","hebrew","hinglish","hungarian","indonesian","italian","kazakh","nepali","norwegian","portuguese","romanian","russian","slovene","spanish","swedish","tajik","turkish"])
if newlines_tabs:
    txt = remove_newlines_tabs(txt)
if remove_html:
    txt = strip_html_tags(txt)
if extra_whitespace:
    txt = remove_whitespace(txt)
if accented_chars:
    txt = accented_characters_removal(txt)
if lowercase:
    txt = lower_casing_text(txt)
if lemm:
    txt = lemmatizer(txt)
if punctuations:
    txt = removing_special_characters(txt)
if remove_stopwords:    
    txt = removing_stopwords(txt,lang)


if txt != "":
    st.header("Results")

    left_column,center_column, right_column = st.columns(3)

    left_column.subheader("1-gram")

    ngram_counts = Counter(ngrams(txt.split(),1))
    df1 = pd.DataFrame.from_dict(ngram_counts.most_common(100))
    df1 = df1.rename(columns={'index':'', 0:'n-gram',1:'count'})
    left_column.dataframe(df1)

    center_column.subheader("2-gram")

    ngram_counts = Counter(ngrams(txt.split(),2))
    df2 = pd.DataFrame.from_dict(ngram_counts.most_common(100))
    df2 = df2.rename(columns={'index':'', 0:'n-gram',1:'count'})
    center_column.dataframe(df2)

    right_column.subheader("3-gram")

    ngram_counts = Counter(ngrams(txt.split(),3))
    df3 = pd.DataFrame.from_dict(ngram_counts.most_common(100))
    df3 = df3.rename(columns={'index':'', 0:'n-gram',1:'count'})
    right_column.dataframe(df3)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='1gram')
        df2.to_excel(writer, sheet_name='2gram')
        df3.to_excel(writer, sheet_name='3gram')
        writer.save()
        st.download_button(
            label="Download Excel Worksheets",
            data=buffer,
            file_name="n-gram.xlsx",
            mime="application/vnd.ms-excel"
        )
    if st.button('See the result of the preprocessing'):
        st.write(txt)