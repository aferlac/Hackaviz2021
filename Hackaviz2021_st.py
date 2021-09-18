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


dffoncqp = pd.read_csv('.\foncier_qp.txt', sep=',')
dffoncqp.drop('nombre_lot', axis=1, inplace=True)
dffoncqp['prix_m_carre']=dffoncqp['valeur_fonciere']/dffoncqp['surface_reelle_bati']
df_geocommune=pd.read_csv('.\geocommune.csv')
for i in range(len(df_geocommune)):
    df_geocommune['geo'][i]=eval(df_geocommune['geo'][i])
df_geoqp = pd.read_csv('.\geoqp.csv')
for i in range(len(df_geoqp)):
    df_geoqp['geo'][i]=eval(df_geoqp['geo'][i])


# In[3]:


dfmutuniq = pd.read_csv('.\foncier_qp_mutation_unique.csv')

##########################################################################################################
#  Construction de foncier_qp_mutation_unique.csv                                                        #
#                                                                                                        #
#  liste_id_mut_uniq = []                                                                                #
#  for i in dffoncqp['id_mutation'].unique():                                                            #
#      if len(dffoncqp[dffoncqp['id_mutation']==i]) == 1:                                                #
#          liste_id_mut_uniq.append(i)                                                                   #
#  dfmutuniq=dffoncqp[(dffoncqp['id_mutation'] == liste_id_mut_uniq[0])]                                 #
#  for i in np.arange(1,len(liste_id_mut_uniq)):                                                         #
#      dfmutuniq = pd.concat([dfmutuniq,dffoncqp[(dffoncqp['id_mutation'] == liste_id_mut_uniq[i])]])    #
#                                                                                                        #
#  dfmutuniq.to_csv('foncier_qp_mutation_unique.csv')                                                    #
#                                                                                                        #
##########################################################################################################

image = Image.open('.\Toulouse_Rue_des_Mouettes_20110414.jpg')


# In[4]:


# Titre de la page Streamlit
st.set_page_config(page_title=' Toulouse-Hackaviz2021 - A.Ferlac ', page_icon=image, layout='wide', initial_sidebar_state='auto')
st.title(" Transactions Immobilières des quartiers prioritaires d'Occitanie - Toulouse Hackaviz 2021")


# In[6]:


st.write('---') 

### Page 1

col1, col2 = st.columns([2,1]) # Séparation de la page en 3 colonnes
col1.header("Introduction")
col1.write("La région Occitanie possède **105 quartiers prioritaires** répartis dans **47 communes** des 12 départements de la région.") 
col1.write("Entre 2016 et 2020, dans ces quartiers prioritaires **28825 transactions immobilières** ont été enregistrées. Ces 28825 transactions ont été traitées par **20418 mutations**. La différence entre les nombres de mutations et de transactions s'explique car près de 18 % de ces mutations concernent plusieurs biens immobiliers. Pour exemple : Les 3 mutations comportant le plus de transactions traitent 40, 44 et 166 biens sur les communes respectivement de Pamiers, Toulouse et Grande Combe + Alès")
col1.write('Les données fournies ne concernent que les transactions des maisons, appartements et locaux industriels, commerciaux ou assimilés. Dans la suite de la présentation les locaux industriels, commerciaux ou assimilés seront appelés "autres".')
col2.image(Image.open("Toulouse_Rue_des_Mouettes_20110414.jpg"), use_column_width=True, caption='Toulouse_Rue_des_Mouettes')
col2.subheader("Nombre de biens par mutation")
data = [82.46, 5.08, 3.75, 8.71]
label= ["1 bien", "4 biens et plus", "3 biens", "2 biens"]
fig, ax = plt.subplots()
ax.pie(x=data, labels=label, autopct='%1.1f%%', startangle=0)
col2.pyplot(fig)
st.write('---') 

#col1, col2, col3 = st.columns(3) # Séparation de la page en 3 colonnes

    
#col2.subheader("Nombre de transactions par commune")
#col2.write("Contient les mutations à biens multiples (28825 mutations)")
#fig1 = plt.figure()
#ax = sns.countplot(x='nom_commune', data=dffoncqp)
#plt.ylim(0,4400)
#plt.xticks(rotation=90, size=8)
#plt.xlabel("")
#plt.ylabel("")
#col2.pyplot(fig1)
    
#col3.subheader("Nombre de mutations à 1 bien par commune")
#col3.write("(16836 mutations)")
#fig2 = plt.figure()
#ax = sns.countplot(x='nom_commune', data=dfmutuniq)
#plt.ylim(0,4400)
#plt.xticks(rotation=90, size=8)
#plt.xlabel("")
#plt.ylabel("")
#col3.pyplot(fig2)

#st.write('---') 
st.header("Quels sont les types de biens mutés par année dans les QP ?")
col1, col2, col3, col4 = st.columns([1,1.25,.5,1]) # Séparation de la page en 3 colonnes
année =[2016, 2017, 2018, 2019, 2020]
   
col1.subheader("Choisissez votre zone à analyser")
choix = col1.radio(label='',
             options=('Région',
                      'Département',
                      'Commune',
                      'Quartier'))
if choix=='Région':
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
    
elif choix=='Département':
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
st.header("Conclusion")
st.write("**3/4 des mutations concernent des appartements. Le quart restant est partagé entre les maisons et les locaux commerciaux ou industriels.**")
st.write("**Baisse des mutations entre 2019 et 2020 : Conséquence du COVID19 ?**")
st.write('---') 
st.write("Application réalisée dans le cadre du concours Hackaviz2021 organisé par Toulouse-Hackaviz avec des notebooks jupyter de la suite Anaconda.")
st.write("Librairies Python utilisées :  pandas, numpy, matplotlib, seaborn, streamlit et folium.")
st.write("J'ai également utilisé du papier, un stylo et la calculatrice de mon portable.")
st.write("Application réalisée par Alain FERLAC à Ceyrat - Puy de Dôme")


# In[ ]:




