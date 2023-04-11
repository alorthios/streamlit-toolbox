import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Page scraper")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

# Fonction de vérification de l'URL
def check_url(url):
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

# Fonction de collecte d'informations
def collect_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title').text.strip() if soup.find('title') else ''
    meta_desc = soup.find('meta', attrs={'name': 'description'})['content'].strip() if soup.find('meta', attrs={'name': 'description'}) else ''
    canonical = soup.find('link', attrs={'rel': 'canonical'})['href'].strip() if soup.find('link', attrs={'rel': 'canonical'}) else ''
    meta_robots = soup.find('meta', attrs={'name': 'robots'})['content'].strip() if soup.find('meta', attrs={'name': 'robots'}) else ''
    h1 = [tag.text.strip() for tag in soup.find_all('h1')] if soup.find_all('h1') else []
    num_links = len(soup.find_all('a'))
    return {'Title': title, 'Meta description': meta_desc, 'Canonical link': canonical, 'Meta robots': meta_robots, 'H1 tags': h1, 'Number of links': num_links}

# Interface utilisateur
st.header("Input")
url = st.text_input("Enter a webpage url :")
if st.button("Run"):
    if check_url(url):
        info_dict = collect_info(url)
        st.header("Output")
        for key, value in info_dict.items():
            st.write(f"{key} : {value}")
    else:
        st.write("Invalid URL.")