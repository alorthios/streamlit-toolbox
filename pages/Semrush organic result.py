import streamlit as st
import pandas as pd
import requests
import io 
import time

empty = []
# Fonction pour télécharger un dataframe au format CSV
def download_csv(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Télécharger le fichier CSV</a>'
    return href

# Fonction pour appeler l'API et stocker les données dans un dataframe
def call_api(api_key, phrase, database, display):
    endpoint = f"https://api.semrush.com/?type=phrase_organic&key={api_key}&phrase={phrase}&export_columns=Dn,Ur,Fk,Fp&database={database}&display_limit={display}"
    response = requests.get(endpoint)
    data = [line.split(';') for line in response.text.split('\n')]
    if data[0][0] == "ERROR 50 :: NOTHING FOUND" :
        empty.append(phrase)
        return pd.DataFrame()
    df = pd.DataFrame(data[1:], columns=data[0])
    df['Position'] = range(1, len(df) + 1)
    df['Keyword'] = phrase
    # set columns order using index
    index = [4,5,0,1,2,3] 
    df = df[[df.columns[i] for i in index]]
    return df

def call_token(api_key):
    endpoint = f"http://www.semrush.com/users/countapiunits.html?key={api_key}"
    response = requests.get(endpoint)
    return response.text

st.set_page_config(layout="wide")
# Titre de l'application
st.title("Semrush organic results")
st.header("Input")
# Champ de saisie pour la clé d'API
api_key = st.text_input("SEMRush API key")
if api_key !="":
    st.write("Number of tokens remaining : " + call_token(api_key))

# Champ de saisie pour la liste de mots clés
keywords = st.text_area("List of keywords (one per line)")

# Sélection de la base de données
databases = ['us','uk','ca','ru','de','fr','es','it','br','au','ar','be','ch','dk','fi','hk','ie','il','mx','nl','no','pl','se','sg','tr','jp','in','hu','af','al','dz','ao','am','at','az','bh','bd','by','bz','bo','ba','bw','bn','bg','cv','kh','cm','cl','co','cr','hr','cy','cz','cd','do','ec','eg','sv','ee','et','ge','gh','gr','gt','gy','ht','hn','is','id','jm','jo','kz','kw','lv','lb','lt','lu','mg','my','mt','mu','md','mn','me','ma','mz','na','np','nz','ni','ng','om','py','pe','ph','pt','ro','sa','sn','rs','sk','si','za','kr','lk','th','bs','tt','tn','ua','ae','uy','ve','vn','zm','zw','ly','mobile-us','mobile-uk','mobile-ca','mobile-de','mobile-fr','mobile-es','mobile-it','mobile-br','mobile-au','mobile-dk','mobile-mx','mobile-nl','mobile-se','mobile-tr','mobile-in','mobile-id','mobile-il','il-ext','tr-ext','dk-ext','no-ext','se-ext','fi-ext','ch-ext','mobile-il-ext','pa','pk','tw','qa']
database = st.selectbox("Select a database", databases)

#Sélection de la profondeur
display = [10,20,30,100]
display = st.selectbox("Select a limit", display)

# Bouton pour lancer l'appel à l'API
if st.button("RUN"):
    st.header("Output")

    progress_text = "Operation in progress. Please wait."
    counter = 0
    my_bar = st.progress(counter, text=progress_text)
    keywords_list = keywords.split('\n')
    tmp_list = []
    for item in keywords_list:
        if item not in tmp_list:
            if item != '':
                tmp_list.append(item)
    keywords_list = tmp_list

    # Boucle sur la liste des mots clés et stockage des résultats dans une liste de dataframes
    dfs = []
    dfpivot = []
    for keyword in  keywords_list:
        df = call_api(api_key, keyword, database, display)
        dfs.append(df)
        if df.empty == False:
            dfpivot.append(df.pivot(index='Keyword', columns='Position', values='Domain').reset_index())
        counter += 100/len(keywords_list)
        my_bar.progress(int(counter), text=progress_text)
    # Concaténation des dataframes en un seul dataframe
    df_all = pd.concat(dfs)
    df_all_pivot = pd.concat(dfpivot)

    # groupe les données par Domain et calcule les fréquences des positions
    grouped = df_all.groupby('Domain')['Position'].apply(lambda x: pd.Series([
        len(x[x == 1]),
        len(x[(x >= 2) & (x <= 3)]),
        len(x[(x >= 4) & (x <= 10)]),
        len(x[(x >= 11) & (x <= 20)]),
        len(x[(x >= 21) & (x <= 30)]),
        len(x[(x >= 31) & (x <= 100)])
    ])).unstack()
    # renomme les colonnes
    grouped.columns = ['Position 1', 'Position 2_3', 'Position 4_10', 'Position 11_20', 'Position 21_30', 'Position 31_100']
    grouped = grouped.sort_values(by=['Position 1'],ascending=False)

    missing = pd.DataFrame (empty, columns = ['Keywords without data'])
    kw = pd.DataFrame (keywords_list, columns = ['Keywords list'])
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        kw.to_excel(writer, sheet_name='KEYWORDS')
        missing.to_excel(writer, sheet_name='MISSING')  
        df_all.to_excel(writer, sheet_name='DATA')
        grouped.to_excel(writer, sheet_name='GROUP')
        df_all_pivot.to_excel(writer, sheet_name='MATRIX')   
    
        writer.save()
        st.download_button(
            label="Download Excel Worksheets",
            data=buffer,
            file_name="semrush-results.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    # Affichage du dataframe
    st.write(df_all)
    #st.write(grouped)

    #https://www.semrush.com/kb/986-api-serp-features