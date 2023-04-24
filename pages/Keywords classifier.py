import streamlit as st
import re
import pandas as pd
import io
import xlsxwriter

max = 4
# Ajouter des champs pour les mots-clés
st.subheader("Enter your keywords (one per row):")
keywords = st.text_area("Keywords")
keywords_list = keywords.split('\n')

# Ajouter des champs pour les combinaisons catégorie/expression
st.subheader("Enter the names and expressions of the category:")

categories = []

col1, col2, col3 = st.columns([1,1,1])

def non_matching_keywords(keywords, categories):
    # Créer une liste de toutes les expressions régulières
    regex_list = []
    for cat in categories :
        if cat["expression"] != "" :
            regex_list.append(re.compile(cat["expression"], re.IGNORECASE))

    # Trouver les mots-clés qui ne correspondent à aucune expression régulière
    non_matching_keywords = [kw for kw in keywords.split("\n") if not any(regex.search(kw) for regex in regex_list)]
    
    # Retourner le nombre de mots-clés qui ne correspondent à aucune expression régulière
    return non_matching_keywords



def count_matching_keywords(keywords, category_expression):
    # Créer l'expression régulière
    regex = re.compile(category_expression, re.IGNORECASE)
    
    # Trouver les mots-clés qui correspondent à l'expression régulière
    matching_keywords = [kw for kw in keywords.split("\n") if regex.search(kw)]
    
    # Retourner le nombre de mots-clés qui correspondent
    return len(matching_keywords)

# Ajouter une combinaison
def add_category(category_name,category_expression):
    categories.append({
        "name": category_name,
        "expression": category_expression
    })


for i in range(1, max):

    category_name = col1.text_input(f"Category name {i}", key=f"name_{i}",help="use descriptive naming")
    category_expression = col2.text_input(f"Category expression {i}", key=f"expression_{i}",help="use a regular expression")
    add_category(category_name,category_expression)
    
    val = str(count_matching_keywords(keywords,category_expression))+"/"+str(len(keywords.split("\n")))
    if category_expression == '':
        val = str(0)+"/"+str(len(keywords.split("\n")))
    if len(keywords) == 0:
        val = str(0)+"/"+str(0)
    col3.text_input(f"Category match {i}", key=f"match_{i}",value=val,disabled=True,help="shows the number of matches with the entered expression")

st.subheader("Keywords without category ("+str(len(non_matching_keywords(keywords,categories)))+"/"+str(len(keywords_list))+")")
for i in non_matching_keywords(keywords,categories):
    st.markdown(i)


# Séparer les mots-clés en une liste
keywords_list = keywords.split("\n")

# Afficher les résultats
st.subheader("Results")
st.write(f"Keywords : {keywords_list}")
for i, category in enumerate(categories):
    st.write(f"Combo {i+1} : {category['name']} / {category['expression']}")




# Créer un buffer pour stocker le fichier Excel en mémoire
output = io.BytesIO()

# Créer un objet Pandas ExcelWriter pour écrire dans le buffer
writer = pd.ExcelWriter(output, engine="xlsxwriter")

# Boucle sur les catégories et écrire chaque catégorie dans une feuille séparée
for cat in categories:
    # Extraire le nom et l'expression régulière de la catégorie
    cat_name = cat["name"]
    cat_regex = re.compile(cat["expression"], re.IGNORECASE)
    
    # Appliquer l'expression régulière aux mots-clés pour trouver les correspondances
    matching_keywords = [kw for kw in keywords.split("\n") if cat_regex.search(kw)]
    
    # Créer un DataFrame Pandas avec les résultats
    df = pd.DataFrame({
        cat_name: [cat_name] * len(matching_keywords),
        "Mots-clés": matching_keywords
    })
    
    # Écrire le DataFrame dans une feuille Excel avec le nom de la catégorie
    df.to_excel(writer, sheet_name=cat_name, index=False)

# Enregistrer et fermer le fichier Excel
writer.save()
output.seek(0)

# Créer un bouton Streamlit pour télécharger le fichier Excel
button_text = "Télécharger XLSX"
st.download_button(
    label=button_text,
    data=output.getvalue(),
    file_name="resultats.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

