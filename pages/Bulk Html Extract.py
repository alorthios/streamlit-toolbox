import requests
import streamlit as st
from bs4 import BeautifulSoup
import time
import pyperclip

# Function to retrieve the content of the <article> HTML tag
def get_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    article = soup.find('article')
    if article:
        return str(article)
    else:
        return 'No article found.'

# User interface
st.title("Retrieve HTML Article Content")

urls = st.text_area("Enter a list of URLs (one per line):", height=200)

if st.button("Run"):
    url_list = urls.split("\n")
    progress_bar = st.progress(0)
    content = ""
    for i, url in enumerate(url_list):
        if url:
            st.write(f"URL : {url}")
            article_content = get_article_content(url)
            content += article_content + "\n\n"
            #st.code(article_content, language='html')
            time.sleep(2)
            progress_bar.progress((i + 1) / len(url_list))
    st.write("Concatenated content:")
    st.text_area("Content:", value=content, height=200)