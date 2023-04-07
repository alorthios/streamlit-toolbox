import requests
import io   
import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd


def is_valid_sitemap(url):
    # Vérifier si l'url est valide
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return False
        # Vérifier si le contenu est bien du XML
        content_type = response.headers.get('Content-Type')
        if not content_type or 'xml' not in content_type:
            return False
        return True
    except:
        return False


def extract_urls_from_sitemap(url):
    response = requests.get(url)
    tree = ET.fromstring(response.content)
    urls = [element.text for element in tree.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    return urls


def main():
    st.title("SITEMAP XML SCRAPER")

    # Entrer l'url du sitemap
    url = st.text_input("Entrez l'URL du sitemap XML")
    left_col, middle_col, right_col = st.columns(3)
    # Bouton RUN pour déclencher le processus
    if left_col.button("RUN"):
        # Vérifier si l'url est valide
        if not is_valid_sitemap(url):
            st.error("L'URL entrée n'est pas un sitemap XML valide")
            return

        # Extraire la liste des URL
        urls = extract_urls_from_sitemap(url)
        df = pd.DataFrame({"URL": urls})

        # Boutons pour télécharger les données sous forme de fichiers CSV et XLSX

        csv = df.to_csv(index=False,header=False).encode('utf-8')

        middle_col.download_button(
        "Download CSV",
        csv,
        "sitemap-url.csv",
        "text/csv",
        key='download-csv'
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='sitemap url',index=False,header=False)
            writer.save()
            right_col.download_button(
                label="Download XLSX",
                data=buffer,
                file_name="sitemap-url.xlsx",
                mime="application/vnd.ms-excel"
            )

        # Afficher la liste des URL sous forme de DataFrame
        st.write("Il y a "+str(len(df))+ " URLS dans le fichier sitemap")

        st.dataframe(df,use_container_width=True)

if __name__ == "__main__":
    main()