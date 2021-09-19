#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image


# In[2]:


# Construction d'un dataframe des transactions immobilieres dans les quartiers prioritaires
dffoncqp = pd.read_csv('./foncier_qp.txt', sep=',')
dffoncqp.drop('nombre_lot', axis=1, inplace=True)
dffoncqp['prix_m_carre']=dffoncqp['valeur_fonciere']/dffoncqp['surface_reelle_bati']

# Construction d'un dataframe des coordonnées géographiques des communes
df_geocommune = pd.read_csv('./geocommune.csv')
for i in range(len(df_geocommune)):
    df_geocommune['geo'][i]=eval(df_geocommune['geo'][i])

# Construction d'un dataframe des coordonnées géographiques des quartiers prioritaires
df_geoqp = pd.read_csv('./geoqp.csv')
for i in range(len(df_geoqp)):
    df_geoqp['geo'][i]=eval(df_geoqp['geo'][i])

# Construction d'un dataframe des mutations d'un seul bien
df_mutation = dffoncqp.merge(right=pd.DataFrame(dffoncqp.groupby(by='id_mutation').size()).reset_index().rename(columns={0: "nombre_bien"}), on='id_mutation')
dfmutuniq = df_mutation[df_mutation['nombre_bien']==1].drop(['nombre_bien'], axis=1)

# Importation de l'image 
image = Image.open('Toulouse_Rue_des_Mouettes_20110414.jpg')

année = [2016, 2017, 2018, 2019, 2020]


# In[3]:


# Titre de la page Streamlit
st.set_page_config(page_title=' Toulouse-Hackaviz2021 - A.Ferlac ', page_icon=image, layout='wide', initial_sidebar_state='auto')
st.title(" Transactions Immobilières des quartiers prioritaires d'Occitanie - Toulouse Hackaviz 2021")

st.write('---') 

col1, col2,col3 = st.columns([1.2,4,1]) # Séparation de la page en 3 colonnes

col1.header("    ")
col1.header("    ")
col1.image(Image.open("Toulouse_Rue_des_Mouettes_20110414.jpg"), use_column_width=True, caption='Toulouse_Rue_des_Mouettes')

col2.header("**Introduction**")
col2.write(
    """
    La région Occitanie possède **105 quartiers prioritaires** répartis dans **47 communes** des 12 départements de la région.\n 
    Entre 2016 et 2020, dans ces quartiers prioritaires **28825 transactions immobilières** ont été enregistrées. 
    Ces 28825 transactions ont été traitées par **20418 mutations**. 
    Une transaction concerne un bien immobilier alors qu'une mutation peut concerner plusieurs biens. \n
    Dans les données fournies près de 18 % de ces mutations concernent plusieurs biens immobiliers. \n
    Pour exemple : Les 3 mutations comportant le plus de transactions traitent 40, 44 et 166 biens sur les communes 
    respectivement de Pamiers, Toulouse et Grande Combe + Alès").\n
    Les données fournies ne concernent que les transactions des maisons, appartements et locaux industriels, commerciaux ou assimilés. 
    Dans la suite de la présentation les locaux industriels, commerciaux ou assimilés seront appelés "autres".
    """)

col3.subheader("Nombre de biens par mutation")
A1 = pd.DataFrame(dffoncqp.groupby(by='id_mutation').size()).reset_index().rename(columns={0: "nombre"})
A2 = pd.DataFrame(A1.groupby('nombre').size()).reset_index().rename(columns={"nombre":"nombre_transaction", 0: "count"})
A2['class'] = pd.cut(A2['nombre_transaction'],
                     bins=[0,1,2,3,200],
                     labels=("1 bien","2 biens", "3 biens", "4 biens et plus"))
A3 = pd.DataFrame(A2.groupby(by='class').sum()).reset_index()

fig, ax = plt.subplots()
ax.pie(A3['count'], labels=A3['class'], autopct='%1.1f%%', startangle=0)
col3.pyplot(fig)

st.write('---') 

st.subheader("**Quels sont les types de biens mutés par année dans les QP ?**")

col1, col2, col3, col4 = st.columns([1,1.25,.5,1]) # Séparation de la page en 4 colonnes
   
col1.subheader("Choisissez votre zone à analyser")
choix = col1.radio(label='',
             options=('Région',
                      'Département',
                      'Commune',
                      'Quartier'))
if choix == 'Région':
    ### Graphe mutations par année et type de local
    y1,y2,y3 = [],[],[]
    for j in année:
        y1.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Appartement')]))
        y2.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Maison')]))
        y3.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Local industriel. commercial ou assimilé')]))
    fig, ax = plt.subplots()
    ax.stackplot(année,y1, y2, y3, labels=['Appart.','Maison','Autre'])
    plt.legend(loc='lower right')
    plt.xticks(ticks=année)
    col2.pyplot(fig)
    
elif choix == 'Département':
    ### Listes a choix multiples départements
    choix_départ=col1.selectbox(label='Département',
                                options=dffoncqp['nom_departement'].sort_values().unique())
    
    ### Graphe mutations par année et type de local
    y1,y2,y3 = [],[],[]
    for j in année:
        y1.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Appartement') &
                              (dffoncqp['nom_departement']==choix_départ)]))
        y2.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Maison') &
                              (dffoncqp['nom_departement']==choix_départ)]))
        y3.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Local industriel. commercial ou assimilé') &
                              (dffoncqp['nom_departement']==choix_départ)]))
    fig, ax = plt.subplots()
    ax.stackplot(année,y1, y2, y3, labels=['Appart.','Maison','Autre'])
    plt.legend(loc='lower right')
    plt.xticks(ticks=année)
    col2.pyplot(fig)
    
    ### Carte indiquant l'emplacement du département
    with col3:
        map = folium.Map([dffoncqp[(dffoncqp['nom_departement']==choix_départ)]['latitude'].mean(),
                                dffoncqp[(dffoncqp['nom_departement']==choix_départ)]['longitude'].mean()], zoom_start=9)
        folium_static(map) # Affichage de la carte dans Streamlit


elif choix=='Commune':
    ### Listes a choix multiples départements et communes
    choix_départ=col1.selectbox(label='Département',
                            options=dffoncqp['nom_departement'].sort_values().unique())
    choix_commune=col1.selectbox(label='Commune',
                             options=dffoncqp[dffoncqp['nom_departement']==choix_départ]['nom_commune'].
                             sort_values().unique())

    ### Graphe mutations par année et type de local
    y1,y2,y3 = [],[],[]
    for j in année:
        y1.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Appartement') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune)]))
        y2.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Maison') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune)]))
        y3.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Local industriel. commercial ou assimilé') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune)]))
    fig, ax = plt.subplots()
    ax.stackplot(année,y1, y2, y3, labels=['Appart.','Maison','Autre'])
    plt.legend(loc='lower right')
    plt.xticks(ticks=année)
    col2.pyplot(fig)
    
    ### Carte indiquant l'emplacement de la commune
    with col3:
        map = folium.Map([dffoncqp[(dffoncqp['nom_departement']==choix_départ)  &
                                  (dffoncqp['nom_commune']==choix_commune)]['latitude'].mean(),
                                dffoncqp[(dffoncqp['nom_departement']==choix_départ)  &
                                  (dffoncqp['nom_commune']==choix_commune)]['longitude'].mean()], zoom_start=10)
        folium.vector_layers.Polygon(locations=df_geocommune[df_geocommune['nom_commune']==choix_commune]['geo'],
                                         fill_color='blue').add_to(map)
        folium_static(map) # Affichage de la carte dans Streamlit

elif choix=='Quartier':
    ### Listes a choix multiples départements, communes et quartiers
    choix_départ=col1.selectbox(label='Département',
                            options=dffoncqp['nom_departement'].sort_values().unique())
    choix_commune=col1.selectbox(label='Commune',
                             options=dffoncqp[dffoncqp['nom_departement']==choix_départ]['nom_commune'].
                             sort_values().unique())
    choix_qp=col1.selectbox(label='Quartier Prioritaire',
                        options=dffoncqp[(dffoncqp['nom_departement']==choix_départ) &
                                          (dffoncqp['nom_commune']==choix_commune)]['nom_qp'].
                        sort_values().unique())

    ### Graphe mutations par année et type de local
    y1,y2,y3 = [],[],[]
    for j in année:
        y1.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Appartement') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune) &
                              (dffoncqp['nom_qp']==choix_qp)]))
        y2.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Maison') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune) &
                              (dffoncqp['nom_qp']==choix_qp)]))
        y3.append(len(dffoncqp[(dffoncqp['annee_mutation']==j) &
                           (dffoncqp['type_local']=='Local industriel. commercial ou assimilé') &
                              (dffoncqp['nom_departement']==choix_départ) &
                              (dffoncqp['nom_commune']==choix_commune) &
                              (dffoncqp['nom_qp']==choix_qp)]))
    fig, ax = plt.subplots()
    ax.stackplot(année,y1, y2, y3, labels=['Appart.','Maison','Autre'])
    plt.legend(loc='lower right')
    plt.xticks(ticks=année)
    col2.pyplot(fig)
    
    ### Carte indiquant l'emplacement du quartier
    with col3:
        map = folium.Map([dffoncqp[(dffoncqp['nom_departement']==choix_départ) &
                                  (dffoncqp['nom_commune']==choix_commune) &
                                  (dffoncqp['nom_qp']==choix_qp)]['latitude'].mean(),
                                dffoncqp[(dffoncqp['nom_departement']==choix_départ)  &
                                  (dffoncqp['nom_commune']==choix_commune) &
                                  (dffoncqp['nom_qp']==choix_qp)]['longitude'].mean()], zoom_start=12)
        folium.vector_layers.Polygon(locations=df_geoqp[(df_geoqp['nom_qp']==choix_qp) &
                                                        (df_geoqp['nom_commune']==choix_commune)]['geo'],
                                         fill_color='blue').add_to(map)
        folium_static(map) # Affichage de la carte dans Streamlit

st.write('---') 

st.subheader("**Comparaison des mutations des appartements**")
st.write("Cette comparaison concerne les mutations à un seul bien.")

liste_etude_appart = ['annee_mutation','nom_departement', 'nom_commune', 'nom_qp', 'nombre_pieces_principales',
           'type_local', 'surface_reelle_bati', 'prix_m_carre']

B1 = pd.DataFrame(np.around(dfmutuniq[liste_etude_appart][dfmutuniq[liste_etude_appart]['type_local']=='Appartement'].groupby(['annee_mutation',
                'nom_departement', 'nom_commune', 'nombre_pieces_principales','type_local']).mean())).reset_index().drop(columns='type_local')

col1, col2, col3, col4, col5, col6, col7 = st.columns([.2,2,.5,.7,.2,2,.2])
select1=col2.multiselect(label='Choisissez les communes (6 maximum)',
                         options=dfmutuniq['nom_commune'].sort_values().unique(),
                         default=['Nîmes','Toulouse', 'Montpellier', 'Perpignan', 'Béziers'])
if len(select1)>6:
    col2.write('Corriger le nombre de communes. 6 maximum')
select2=col4.radio(label="Nombre de pièces", options=[1, 2, 3, 4])
select3=col6.multiselect(label='Choisissez les années', options=année, default=année)


aff=pd.DataFrame(columns=B1.columns)
for ville in select1[0:6]:
    for années in select3:
        aff=pd.concat([aff,B1[(B1['nom_commune'] == ville) & (B1['annee_mutation'] == années)]], axis=0)
aff.rename(columns={"annee_mutation": "année"}, inplace=True)
    
col1, col2, col3, col4, col5 = st.columns([.5,2,.5,2,.5]) # Séparation de la page en 3 colonnes

col2.subheader("Prix au m² en €")
fig, ax = plt.subplots()
sns.barplot(data=aff[aff['nombre_pieces_principales']==select2], y='prix_m_carre', x='nom_commune', hue='année', palette="Blues")
plt.xlabel("")
plt.ylabel("")
col2.pyplot(fig)

col4.subheader("surface moyenne en m²")
fig, ax = plt.subplots()
sns.barplot(data=aff[aff['nombre_pieces_principales']==select2], y='surface_reelle_bati', x='nom_commune', hue='année', palette="Blues")
plt.xlabel("")
plt.ylabel("")
col4.pyplot(fig)
st.write('---')
st.header("**Conclusion**")
st.write("3/4 des mutations concernent des appartements. Le quart restant est partagé entre les maisons et les locaux commerciaux ou industriels.")
st.write("On constate :")
st.write("""    
    * une baisse du nombre des mutations entre 2019 et 2020 : Conséquence du COVID19 ? \n
    * une augmentation des prix depuis 2016 : Mise en place de la politique des quartiers prioritaires ? \n
    * Les surfaces des appartements sont plus élevées dans les petites agglomérations.
    """)

st.write('---') 
st.write("""
    Application réalisée dans le cadre du concours Hackaviz2021 organisé par Toulouse-Hackaviz avec des notebooks jupyter de la suite Anaconda.\n
    Librairies Python utilisées :  pandas, numpy, matplotlib, seaborn, streamlit et folium. \n
    J'ai également utilisé du papier, un stylo et la calculatrice de mon portable.\n
    Application réalisée par Alain FERLAC à Ceyrat - Puy de Dôme.
    """)


# In[ ]:




