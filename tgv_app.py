import requests
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
import streamlit as st
from PIL import Image



############### MAIN Functions ########################

def df_init():
    url = 'https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=10000&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine=PARIS+(intramuros)&refine.destination=LA+ROCHELLE+VILLE'

    response_API_tgv = requests.get(url)

    data = response_API_tgv.text
    parse_json = json.loads(data)


    arr = []
    for i in range(len(parse_json['records'])):
        record = parse_json['records'][i]['fields']
        date = record['date']
        heure_arrivee = record['heure_arrivee']
        heure_depart = record['heure_depart']
        origine = record['origine']
        destination = record['destination']

        data_point = [origine, destination, date, heure_depart, heure_arrivee]
        arr.append(data_point)

    df = pd.DataFrame(arr, columns = ['origine', 'destination', 'date','heure_depart', 'heure_arrivee'])
    return df



def param(df_ville_origine,df_ville_destination):
     values_origine = df_ville_origine.values.flatten()
     option_origine = st.sidebar.selectbox(
          "Ville d'origine",
          values_origine,
          index = list(values_origine).index('PARIS (intramuros)'))


     values_destination = df_ville_destination.values.flatten()
     option_destination = st.sidebar.selectbox(
          "Ville de destination",
          values_destination,
          index = list(values_destination).index('LA ROCHELLE VILLE'))


     today = datetime.now()
     option_date = st.sidebar.date_input(
          "Date de départ",
          today,
          min_value = today,
          max_value = today + timedelta(days=29)
          )

     bouton_launch_search=st.sidebar.button("Rechercher")
     
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write("Me contacter [Linkedin](https://www.linkedin.com/in/pierre-louis-danieau/)")
     st.sidebar.write(" ")
     st.sidebar.write("**©️ Copyright 2022 - Pierre-Louis Danieau**")

     return option_origine,option_destination,option_date,bouton_launch_search

def dataframe_train(option_origine,option_destination,option_date):
     day = option_date.day
     month = option_date.month
     year = option_date.year

     url = 'https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=10000&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine={}&refine.date={}%2F{}%2F{}&refine.destination={}'.format(option_origine,year,month,day,option_destination)
     response_API_tgv = requests.get(url)

     data = response_API_tgv.text
     parse_json = json.loads(data)


     arr = []
     for i in range(len(parse_json['records'])):
          record = parse_json['records'][i]['fields']
          date = record['date']
          heure_arrivee = record['heure_arrivee']
          heure_depart = record['heure_depart']
          origine = record['origine']
          destination = record['destination']

          data_point = [origine, destination, date, heure_depart, heure_arrivee]
          arr.append(data_point)

     df = pd.DataFrame(arr, columns = ['origine', 'destination', 'date','heure_depart', 'heure_arrivee'])
     return df


def formulaire():
    html='<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSexZO8N0YxIQN0wKRdgyQSsI0Q-0xGk0a3A-aXpZBApBGdfqg/viewform?embedded=true" width="640" height="499" frameborder="0" marginheight="0" marginwidth="0">Chargement…</iframe>'
    st.markdown(html, unsafe_allow_html=True)




############### MAIN Programm #########################


if __name__ == "__main__":
     image = Image.open('photo_train.jpg')
     
     col1_first, col2_first = st.columns(2)

     with col1_first:
          st.markdown("<h2 style='color: RoyalBlue;'>Maxplorateur App</h2>", unsafe_allow_html=True)
          st.write("""
               **L'ensemble des trains éligibles à l'abonnement TGV max en un seul endroit !**
               
               Définissez vos critères dans la barre de gauche !
               """)

          
     with col2_first:
          st.image(image, caption='Photo by Ankush Minda', use_column_width='auto')
     
     st.write(' ')
     col1, col2, col3 = st.columns(3)


     df_ville_origine = pd.read_csv('ville_origine.csv')
     df_ville_destination = pd.read_csv('ville_destination.csv')
     del df_ville_origine['Unnamed: 0']
     del df_ville_destination['Unnamed: 0']


     st.sidebar.markdown("<h2 style='text-align: center; color: RoyalBlue;'>Critères</h2>", unsafe_allow_html=True)


     option_origine,option_destination,option_date,bouton_launch_search = param(df_ville_origine,df_ville_destination)


     if bouton_launch_search == True:
          df_train_filter = dataframe_train(option_origine,option_destination,option_date)
          if df_train_filter.shape[0] == 0:
               st.write(' ')
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Mince..  🙁 </h4>", unsafe_allow_html=True)
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Aucun trains de prévus en TGV max pour l'instant avec ces critères.</h4>", unsafe_allow_html=True)
               st.markdown("<h6 style='text-align: center; color: RoyalBlue;'>Réessaye demain vers 9h-10h ! .</h6>", unsafe_allow_html=True)
               st.write(' ')
               st.write(' ')
               with st.expander("🚆 Informations importantes sur les trains"):
                    st.write("""
                    ⚠️ Les trains affichés sont les trains **élligibles** à l'abonnement TGV Max. 

                    Cependant, il arrive (de temps en temps) que le prix du billet ne soit tout de même pas à 0 € sur le site de la SNCF. 

                    En effet, lorsque la demande est trop élevée, la SNCF fait payer les places alors même que le train est éligible à TGV Max.

                    De plus les données de l'application sont mise à jour tous les matins vers 9h. Si vous vous connectez trop tardivement dans la journée, il se peut que les places ne soient plus disponibles.

                    Je suis actuellement en train de résoudre ces problèmes pour : 

                         - Afficher uniquement les places à 0 €
                    
                         - Mise à jour plusieurs fois par jours des trains.
                    
                         - Mise en place d'une alerte par mail lorsqu'un une place est disponible.
                    
                    Partager ou parler autour de vous de cette application me permettra de gagner en visibilité auprès de la SNCF afin d'obtenir davantage de données sur les trains TGV Max et ainsi améliorer l'app !
                    
                    Merci beaucoup 🙂
                    """)
               with st.expander("📧 Recevez une alerte par mail lorsque qu'une place se libère !"):
                    formulaire()

          else:
               st.markdown("<h4 style='color: RoyalBlue;'>Voici la liste des trains dispos :  🎉🎉🎉</h4>", unsafe_allow_html=True)
               df_train_filter.columns = ["Origine", "Destination", "Date", "Heure de départ", "Heure d'arrivée"]
               st.dataframe(df_train_filter, 1000)
               st.write(' ')
               with st.expander("🚆 Informations importantes sur les trains"):
                    st.write("""
                    ⚠️ Les trains affichés sont les trains **élligibles** à l'abonnement TGV Max. 

                    Cependant, il arrive (de temps en temps) que le prix du billet ne soit tout de même pas à 0 € sur le site de la SNCF. 

                    En effet, lorsque la demande est trop élevée, la SNCF fait payer les places alors même que le train est éligible à TGV Max.

                    De plus les données de l'application sont mise à jour tous les matins vers 9h. Si vous vous connectez trop tardivement dans la journée, il se peut que les places ne soient plus disponibles.

                    Je suis actuellement en train de résoudre ces problèmes pour : 

                         - Afficher uniquement les places à 0 €
                    
                         - Mise à jour plusieurs fois par jours des trains.
                    
                         - Mise en place d'une alerte par mail lorsqu'un une place est disponible.
                    
                    Partager ou parler autour de vous de cette application me permettra de gagner en visibilité auprès de la SNCF afin d'obtenir davantage de données sur les trains TGV Max et ainsi améliorer l'app !
                    
                    Merci beaucoup 🙂
                    """)
               with st.expander("📧 Recevez une alerte par mail lorsque qu'une place se libère !"):
                    formulaire()



          with col1:
               st.subheader('Origine')
               st.write(option_origine)
          with col2:
               st.subheader('Destination')
               st.write(option_destination)
          with col3:
               st.subheader('Date')
               st.write(option_date, ' : aaaa-mm-jj ')
