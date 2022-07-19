import requests
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
import streamlit as st
from PIL import Image
from dateutil import parser
import locale
#from streamlit.scriptrunner import get_script_run_ctx as get_report_ctx




############### MAIN Functions ########################


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
     placeholder = st.sidebar.empty()
     option_date = placeholder.date_input(
          "Date de départ",
          today,
          min_value = today,
          max_value = today + timedelta(days=29)
          )
          
     all_dates = st.sidebar.checkbox('Toutes les places dispo sur 30 jours')

     if all_dates == True:
          placeholder.empty()

     bouton_launch_search=st.sidebar.button("Rechercher")
     

     st.sidebar.write(" ")
     st.sidebar.write(" ")
     st.sidebar.write("Me contacter [Linkedin](https://www.linkedin.com/in/pierre-louis-danieau/)")
     st.sidebar.write("**©️ Copyright 2022 - Pierre-Louis Danieau**")

     return option_origine,option_destination,option_date,all_dates,bouton_launch_search

#@st.cache
#def mis_a_jour(id):
#     locale.setlocale(locale.LC_TIME,'')
#     url = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=1&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card"
#     response_API_tgv = requests.get(url)
#     data = response_API_tgv.text
#     parse_json = json.loads(data)
#     mis_a_jour= parse_json['records'][0]['record_timestamp']
#     mis_a_jour_date = parser.parse(mis_a_jour)
#     str_maj = mis_a_jour_date.strftime("%A %d %B %Y à %H:%M")
#     return str_maj

def dataframe_train(option_origine,option_destination,option_date,all_dates):
     day = option_date.day
     month = option_date.month
     year = option_date.year

     if all_dates == False:
          # Specific dates
          url = 'https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=10000&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine={}&refine.date={}%2F{}%2F{}&refine.destination={}'.format(option_origine,year,month,day,option_destination)
     else :
          # All dates
          url = 'https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=10000&sort=-date&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine={}&refine.destination={}&refine.od_happy_card=OUI'.format(option_origine,option_destination)
     
     response_API_tgv = requests.get(url)
     data = response_API_tgv.text
     parse_json = json.loads(data)

     arr = []
     for i in range(len(parse_json['records'])):
          record = parse_json['records'][i]['fields']
          date = record['date']
          heure_arrivee = datetime.strptime(record['heure_arrivee'], '%H:%M')
          heure_depart = datetime.strptime(record['heure_depart'], '%H:%M')
          origine = record['origine']
          destination = record['destination']
          tgv_jeune_senior = (record['od_happy_card'])
          data_point = [origine, destination, date, heure_depart, heure_arrivee, tgv_jeune_senior]
          arr.append(data_point)
     
     df = pd.DataFrame(arr, columns = ['origine', 'destination', 'date','heure_depart', 'heure_arrivee','places disponibles'])
     df = df.sort_values(by=['date','heure_depart'])
     df['heure_arrivee'] = df['heure_arrivee'].apply(lambda x : x.strftime("%H:%M")+4*' ')
     df['heure_depart'] = df['heure_depart'].apply(lambda x : x.strftime("%H:%M")+4*' ')
     df['places disponibles'] = df['places disponibles'].apply(lambda x: 'PEUT ÊTRE'+4*' ' if x =="NON" else 'OUI'+10*' ')
     df = df.reset_index(drop=True)
     return df


def formulaire():
    html='<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSexZO8N0YxIQN0wKRdgyQSsI0Q-0xGk0a3A-aXpZBApBGdfqg/viewform?embedded=true" width="640" height="499" frameborder="0" marginheight="0" marginwidth="0">Chargement…</iframe>'
    st.markdown(html, unsafe_allow_html=True)

def color_df(val):
     if val =="OUI"+10*' ':
          color = '#8DEF7B'
     else :
          color = '#FC9F60'
     return f'background-color: {color}'



############### MAIN Programm #########################


if __name__ == "__main__":
     locale.setlocale(locale.LC_TIME,'')
     st.set_page_config(
     page_title="Maxplorateur",
     page_icon="🚅",
     layout="wide",
     initial_sidebar_state="expanded",
     )

     ## Hide menu
     hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
     st.markdown(hide_menu_style, unsafe_allow_html=True)
     ## End hide menu


     image = Image.open('photo_train.jpg')
     
     #ctx = get_report_ctx()
     #id = ctx.session_id
     
     col1_first, col2_first = st.columns(2)
     #str_maj = mis_a_jour(id)

     with col1_first:
          st.markdown("<h2 style='color: RoyalBlue;'>Maxplorateur App - Recherche</h2>", unsafe_allow_html=True)
          st.write("""
               **L'ensemble des trains éligibles à l'abonnement TGV max !**
               
               Définissez vos critères dans la barre de gauche !
               """)
          #st.markdown("<p style='color: RoyalBlue;'>Mise à jour des trains le : {} </p>".format(str_maj), unsafe_allow_html=True)
          st.write("**Ce site évolue et ne sera bientôt plus accessible via cet URL ! Pour continuer à chercher des TGV Max, connecte toi ici : [Maxplorateur](https://maxplorateur.com/) 😉**")


          
     with col2_first:
          st.image(image, caption='Photo by Ankush Minda', width = 350)
     
     st.write(' ')
     col1, col2, col3 = st.columns(3)


     df_ville_origine = pd.read_csv('ville_origine.csv')
     df_ville_destination = pd.read_csv('ville_destination.csv')
     del df_ville_origine['Unnamed: 0']
     del df_ville_destination['Unnamed: 0']

     st.sidebar.markdown("# 1️⃣ - Recherche de TGV Max")


     option_origine,option_destination,option_date,all_dates,bouton_launch_search = param(df_ville_origine,df_ville_destination)


     if bouton_launch_search == True:
          df_train_filter = dataframe_train(option_origine,option_destination,option_date,all_dates)
          if df_train_filter.shape[0] == 0:
               st.write(' ')
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Mince..  🙁 </h4>", unsafe_allow_html=True)
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Aucun trains éligibles à TGV max pour l'instant avec ces critères.</h4>", unsafe_allow_html=True)
               st.markdown("<h6 style='text-align: center; color: RoyalBlue;'>Réessaye demain vers 9h-10h ! .</h6>", unsafe_allow_html=True)
               st.write(' ')
               st.write(' ')

          else:
               st.markdown("<h4 style='color: RoyalBlue;'>Voici la liste des trains éligibles :  🎉🎉🎉</h4>", unsafe_allow_html=True)
               df_train_filter.columns = ["Origine", "Destination", "Date", "Heure de départ", "Heure d'arrivée", "Places disponibles"]
               st.dataframe(df_train_filter.style.applymap(color_df, subset=[df_train_filter.columns[-1]]),3000)
               st.write(' ')
          
          with st.expander("🚆 Informations importantes sur les trains"):
               st.write("""
               ⚠️ Les trains affichés sont les trains **élligibles** à l'abonnement TGV Max. 

               Or, tous les trains éligibles à TGV Max n'ont plus forcément de places diponibles à 0 €.
          
               C'est pourquoi tu retrouveras le champ "Places disponibles" dans la liste des trains proposés avec comme valeur :

                    - "OUI", lorsqu'il reste des places disponibles en TGV Max à 0 €.

                    - "PEUT ETRE", lorsque je ne suis pas certain qu'il reste des places gratuites. 
                    
               En effet je n'ai malheureusement pas encore accès à toutes les données sur les TGV max de la SNCF, il y a donc des trains pour lesquels je ne sais pas si il reste des places dispos ou non.
          
               De plus, les données de l'application sont mises à jour une fois par jour en début de matinée. Et il se peut que la SNCF modifie plusieurs fois par jour l'éligibilité et / ou la disponibilité d'un train TGV Max. Il peut donc y avoir des inexactitudes entre ce que l'application renvoie et ce qui est proposé sur le site de la SNCF.  
               
               C'est pourquoi il vaut mieux se connecter le **matin** sur l'application Maxplorateur !

               Mais pas de panique, je suis actuellement en train de résoudre ces problèmes !
               
               Partager ou parler autour de toi de cette application me permettra de gagner en visibilité auprès de la SNCF afin d'obtenir davantage de données sur les trains TGV Max et ainsi améliorer l'app Maxplorateur !
               
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
               if all_dates == True : 
                    st.write('3O prochains jours')
               else:
                    st.write(option_date.strftime("%A %d %B %Y"))
