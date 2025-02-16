import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Configuration de la page
st.set_page_config(page_title="Accueil Michka", page_icon=":robot_face:")

# Image de fond ou logo de Michka
image_path_1 = r"C:\Users\MANRESA\Documents\DESC\5_Informatique\Projet Michka\Images\Michka.jpg"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("file://{image_path_1}");
        background-size: cover;
        background-position: center;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align: center; color: #1E90FF; background-color: rgba(255, 255, 255, 0.8); padding: 10px;'>Bienvenue sur Michka</h1>",
    unsafe_allow_html=True)

# Initialiser les variables de session
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'patients_data' not in st.session_state:
    # Simuler une liste de personnes
    data = {
        "Nom": [f"Enfant_{i}" for i in range(1, 31)] + [f"Adolescent_{i}" for i in range(1, 11)] + [f"Adulte_{i}" for i
                                                                                                    in range(1, 11)],
        "Âge": np.random.choice(range(2, 9), 30).tolist() + np.random.choice(range(9, 17),
                                                                             10).tolist() + np.random.choice(
            range(20, 60), 10).tolist(),
        "Niveau Actuel": np.random.choice(["Débutant", "Intermédiaire", "Avancé"], 50).tolist(),
        "Statistiques": [np.random.rand(10).tolist() for _ in range(50)],
        "Évolution": [np.random.rand(10).tolist() for _ in range(50)]
    }
    st.session_state.patients_data = pd.DataFrame(data)


# Fonction pour gérer la connexion
def connexion():
    if not st.session_state.authenticated:
        # Sélection du type d'utilisateur
        user_type = st.radio("Sélectionnez votre profil :", ('Professionnel', 'Particulier'))

        # Mot de passe associé
        password = st.text_input("Entrez le mot de passe :", type="password")

        # Vérification du mot de passe
        if st.button("Accéder"):
            if user_type == 'Professionnel' and password == 'pro':
                st.session_state.user_type = user_type
                st.session_state.authenticated = True
            elif user_type == 'Particulier' and password == 'part':
                st.session_state.user_type = user_type
                st.session_state.authenticated = True
            else:
                st.error("Mot de passe incorrect. Veuillez réessayer.")
    else:
        if st.session_state.user_type == 'Professionnel':
            menu_professionnel()
        elif st.session_state.user_type == 'Particulier':
            menu_particulier()


# Fonction pour le menu professionnel
def menu_professionnel():
    st.write("Bienvenue dans l'espace professionnel de Michka.")

    # Choix du menu
    menu_choice = st.selectbox("Choisissez une option :", ["Nouveau patient", "Calendrier", "Consultation", "Prise de rendez-vous"])

    if menu_choice == "Nouveau patient":
        ajouter_patient()
    elif menu_choice == "Calendrier":
        calendrier_rendez_vous()
    elif menu_choice == "Consultation":
        consulter_patient()
    elif menu_choice == "Prise de rendez-vous":
        prise_de_rendez_vous()


# Fonction pour ajouter un nouveau patient
def ajouter_patient():
    st.subheader("Ajout d'un nouveau patient")
    nom = st.text_input("Nom du patient")
    age = st.number_input("Âge du patient", min_value=0, max_value=100, step=1)
    niveau = st.selectbox("Niveau Actuel", ["Débutant", "Intermédiaire", "Avancé"])
    statistiques = np.random.rand(10).tolist()
    evolution = np.random.rand(10).tolist()

    if st.button("Ajouter"):
        new_patient = {
            "Nom": nom,
            "Âge": age,
            "Niveau Actuel": niveau,
            "Statistiques": statistiques,
            "Évolution": evolution
        }
        st.session_state.patients_data = st.session_state.patients_data.append(new_patient, ignore_index=True)
        st.success("Nouveau patient ajouté avec succès !")


# Fonction pour afficher le calendrier des rendez-vous
def calendrier_rendez_vous():
    st.subheader("Calendrier des rendez-vous")

    # Sélection de l'année
    year = st.selectbox("Sélectionnez l'année :", list(range(1900, datetime.now().year + 1)))

    # Sélection du mois
    month = st.selectbox("Sélectionnez le mois :", list(calendar.month_name)[1:])

    # Calcul des jours fériés (exemple simple pour la France)
    holidays = {
        "Nouvel An": datetime(year, 1, 1),
        "Fête du Travail": datetime(year, 5, 1),
        "Armistice 1945": datetime(year, 5, 8),
        "Fête Nationale": datetime(year, 7, 14),
        "Assomption": datetime(year, 8, 15),
        "Toussaint": datetime(year, 11, 1),
        "Armistice 1918": datetime(year, 11, 11),
        "Noël": datetime(year, 12, 25)
    }

    # Générer le calendrier
    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdates(year, list(calendar.month_name).index(month)))

    # Affecter des rendez-vous
    df = st.session_state.patients_data
    rendez_vous = []

    for index, row in df.iterrows():
        if row["Niveau Actuel"] == "Débutant":
            num_sessions = 20  # Minimum 20 sessions par an
        else:
            num_sessions = 10  # Exemple pour d'autres niveaux

        frequency = np.random.choice([1, 2])  # 1h ou 2h par semaine
        start_date = datetime(year, 1, 1)

        for session in range(num_sessions):
            while start_date.weekday() in [5, 6] or start_date in holidays.values():
                start_date += timedelta(days=1)  # Éviter les week-ends et jours fériés
            rendez_vous.append((row["Nom"], start_date))
            start_date += timedelta(weeks=frequency)

    # Afficher le calendrier
    for day in month_days:
        if day.month == list(calendar.month_name).index(month):
            day_str = day.strftime("%A %d %B %Y")
            if day in holidays.values():
                st.markdown(f"<span style='color:red;'>{day_str} (Férié)</span>", unsafe_allow_html=True)
            else:
                st.write(day_str)

            # Afficher les rendez-vous pour ce jour
            day_appointments = [rdv for rdv in rendez_vous if rdv[1] == day]
            for appointment in day_appointments:
                st.write(f"- Rendez-vous avec {appointment[0]}")

# Fonction pour consulter un patient
def consulter_patient():
    st.subheader("Consultation d'un patient")
    df = st.session_state.patients_data

    # Menu déroulant pour sélectionner une personne
    selected_person = st.selectbox("Sélectionnez une personne :", df["Nom"])

    # Afficher les détails de la personne sélectionnée
    person_details = df[df["Nom"] == selected_person].iloc[0]

    st.write(f"**Nom :** {person_details['Nom']}")
    st.write(f"**Âge :** {person_details['Âge']} ans")
    st.write(f"**Niveau Actuel :** {person_details['Niveau Actuel']}")

    # Graphiques des statistiques d'apprentissage et d'évolution
    st.subheader("Statistiques d'Apprentissage")
    st.bar_chart(person_details["Statistiques"])

    st.subheader("Évolution depuis le Début de l'Enseignement")
    st.line_chart(person_details["Évolution"])

# Fonction pour la prise de rendez-vous
def prise_de_rendez_vous():
    st.subheader("Prise de rendez-vous")
    df = st.session_state.patients_data

    # Sélectionner un patient
    selected_person = st.selectbox("Sélectionnez un patient :", df["Nom"])
    person_index = df[df["Nom"] == selected_person].index[0]

    # Sélectionner une date de rendez-vous
    rdv_date = st.date_input("Sélectionnez la date du rendez-vous", datetime.now())

    # Sélectionner une heure de rendez-vous
    rdv_time = st.selectbox("Sélectionnez l'heure du rendez-vous", [f"{hour}:00" for hour in range(9, 18)])  # Créneaux horaires de 9h à 17h

    # Ajouter le rendez-vous
    if st.button("Ajouter le rendez-vous"):
        st.session_state.patients_data.at[person_index, "Rendez-vous"].append((rdv_date, rdv_time))
        st.success(f"Rendez-vous ajouté pour {selected_person} le {rdv_date.strftime('%d/%m/%Y')} à {rdv_time}")

# Fonction pour le menu particulier
def menu_particulier():
    st.write("Bienvenue dans l'espace particulier de Michka.")
    # Ajoutez ici le code ou la fonction pour afficher le contenu particulier

    # Bouton quitter
    if st.button("Quitter"):
        st.session_state.authenticated = False
        st.session_state.user_type = None


# Appel de la fonction connexion pour démarrer l'application
connexion()

# Note : Assurez-vous que le chemin de l'image est correct et accessible depuis votre machine.