import requests
import json
from datetime import datetime
from datetime import timedelta
import pandas as pd
import streamlit as st
from PIL import Image
import locale
from pymongo import MongoClient




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

def create_mail(records):
     st.caption("Si tu souhaites recevoir une alerte par mail dès qu'une place se libère, renseigne ton adresse mail juste en-dessous ! :sunglasses:")
     st.caption(f"Rappel de ta recherche :   Ville de départ ➡️ :blue[{option_origine}],   Ville d'arrivée ➡️ :blue[{option_destination}],   Date ➡️ :blue[{option_date}]")
     email_type = st.text_input('Ton adresse email : ', key=1, value="", placeholder="prenom.nom@gmail.com")
     if email_type != '':
          find_another_alert = False
          for alert_find in records.find({"email":email_type, 'ville_depart':option_origine, 'ville_destination':option_destination, 'date':option_date.strftime("%Y-%m-%d")}):
               find_another_alert = True
               break
          
          st.markdown(f"<p style='color: RoyalBlue; font-weight: bold;'>Super ! Tu recevras une alerte dès qu'un nouveau TGV Max sera dispo ! Check régulièrement tes mails sur : {email_type} 🙂</p>", unsafe_allow_html=True)
          st.markdown("<p style='color: RoyalBlue; font-weight: bold;'>Tu peux également regarder la liste de tes alertes dans l'onglet : <i>L'ensemble de mes alertes</i> ! </p>", unsafe_allow_html=True)
          st.balloons()
          alert = {
               'ville_depart':option_origine,
               'ville_destination':option_destination,
               'date':option_date.strftime("%Y-%m-%d"),
               'email':email_type,
               'time_added':datetime.now().strftime("%Y,%m,%d, %H:%M:%S")
               
          }
          if not find_another_alert:
               records.insert_one(alert)
          else:
               return

def check_mail(records):
     st.caption("Si tu souhaites connaître l'ensemble de tes alertes en cours, renseigne ton adresse email juste en dessous ! :sunglasses:")
     st.caption("Elles seront supprimées au bout de 30 jours ! ")
     email_type = st.text_input('Ton adresse email : ', key=2, value="", placeholder="prenom.nom@gmail.com")
     if email_type != '':
          list_alert = []
          find_alert = False

          for alert in records.find({"email":email_type}):
               list_alert.append(alert)
               find_alert = True
               
          if find_alert:
               st.markdown("<p style='color: RoyalBlue; font-weight: bold;'>Voici la liste des alertes associéées à ta boîte mail ! Elles seront automatiquement supprimées au bout de 30 jours 🙂</p>", unsafe_allow_html=True)
               for alert in list_alert:
                    alert = {key: alert[key] for key in sorted(alert.keys() & {'ville_destination', 'date', 'email', 'ville_depart'})}
                    st.write(alert)

          else :
               st.markdown("<p style='color: RoyalBlue; font-weight: bold;'>Aucune alerte a été trouvé avec cette adresse mail... 😕 Tu peux en créer une dans l'onglet <i>Ajoute une nouvelle alerte</i> ! </p>", unsafe_allow_html=True)

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


     if 'option_origine' not in st.session_state:
          st.session_state['option_origine'] = False
     
     if 'option_destination' not in st.session_state:
          st.session_state['option_destination'] = False
     
     if 'option_date' not in st.session_state:
          st.session_state['option_date'] = False
     
     if 'all_dates' not in st.session_state:
          st.session_state['all_dates'] = False
     


     image = Image.open('photo_train.jpg')
     
     email_type = ''
     col1_first, col2_first = st.columns(2)

     with col1_first:
          st.markdown("<h2 style='color: RoyalBlue;'>Maxplorateur App - Recherche</h2>", unsafe_allow_html=True)
          st.write("""
               **L'ensemble des trains éligibles à l'abonnement TGV max !**
               
               Définissez vos critères dans la barre de gauche !
               """)
          
     with col2_first:
          st.image(image, caption='Photo by Ankush Minda', width = 250)
     
     st.write(' ')

     col1, col2, col3 = st.columns(3)


     df_ville_origine = pd.read_csv('ville_origine.csv')
     df_ville_destination = pd.read_csv('ville_destination.csv')
     del df_ville_origine['Unnamed: 0']
     del df_ville_destination['Unnamed: 0']

     st.sidebar.markdown("# 1️⃣ - Recherche de TGV Max")


     option_origine,option_destination,option_date,all_dates,bouton_launch_search = param(df_ville_origine,df_ville_destination)

     if st.session_state.get('bouton_launch_search') == False:
          st.session_state['bouton_launch_search'] = bouton_launch_search

     if (st.session_state['option_origine'] != option_origine) or (st.session_state['option_destination'] != option_destination) or (st.session_state['option_date'] != option_date) or (st.session_state['all_dates'] != all_dates):
          st.session_state['bouton_launch_search'] = False
          st.session_state['option_origine'] = option_origine
          st.session_state['option_destination'] = option_destination
          st.session_state['option_date'] = option_date
          st.session_state['all_dates'] = all_dates


     if st.session_state['bouton_launch_search'] == True:
          df_train_filter = dataframe_train(option_origine,option_destination,option_date,all_dates)
          if df_train_filter.shape[0] == 0:
               st.write(' ')
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Mince..  🙁 </h4>", unsafe_allow_html=True)
               st.markdown("<h4 style='text-align: center; color: RoyalBlue;'>Aucun trains éligibles à TGV max pour l'instant avec ces critères.</h4>", unsafe_allow_html=True)
               st.markdown("<h6 style='text-align: center; color: RoyalBlue;'>Crée toi une alerte juste en dessous ! 🚨</h6>", unsafe_allow_html=True)
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

                    - "PEUT ETRE", lorsqu'il reste que très peu de places gratuites et que la dernière vient peut-être tout juste d'être vendue !  
               
                """)


          if all_dates ==False:
               st.markdown("<h4 style='color: RoyalBlue;'>Tu souhaites être alerté quand une place se libère ? 🚨🚨🚨</h4>", unsafe_allow_html=True)

               tab1, tab2 = st.tabs(["Ajoute une nouvelle alerte", "L'ensemble de mes alertes"])
               mongo_db_adress = st.secrets["mongo_db_adress"]
               client = MongoClient(mongo_db_adress)
               db = client.get_database('tgv_db')
               records = db.alert_record
               with tab1:
                    create_mail(records)
               with tab2:
                    check_mail(records)


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

