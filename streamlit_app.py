#------------------------------------------------------------------------------------------------------------
#--------------------------------------MICHKA MENU WEB PROFESSIONNEL-----------------------------------------
#--------------------------------------Str_Web_2TAB_PRO_Michka_V11.py----------------------------------------
#------------------------------------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 📂 Chemins des fichiers de données
file_path_patients = r"./BDD_Michka.csv"
file_path_rdv = r"./RDV.csv"
file_purge_rdv = r"./db/Purge_RDV.csv"

# 📂 Chemins des fichiers de données perso
#file_path_patients = r"C:\Users\MANRESA\Documents\DESC\5_Informatique\Projet Michka\BDD_Michka\BDD_Michka.csv"
#file_path_rdv = r"C:\Users\MANRESA\Documents\DESC\5_Informatique\Projet Michka\BDD_Michka\RDV.csv"
#file_purge_rdv = r"C:\Users\MANRESA\Documents\DESC\5_Informatique\Projet Michka\BDD_Michka\Purge_RDV.csv"


# Fonction pour reconstruire Date_RDV au format français
def rebuild_date_rdv(df):
    if {'JRDV', 'MRDV', 'ARDV'}.issubset(df.columns):
        mask_nan_dates = df['Date_RDV'].isna()
        if mask_nan_dates.any():
            df.loc[mask_nan_dates, 'Date_RDV'] = pd.to_datetime(
                df.loc[mask_nan_dates, ['ARDV', 'MRDV', 'JRDV']].rename(
                    columns={'ARDV': 'year', 'MRDV': 'month', 'JRDV': 'day'}), errors='coerce'
            ).dt.strftime('%d/%m/%Y')

# Charger les données de rendez-vous
try:
    rdv_data = pd.read_csv(file_path_rdv, sep=',', encoding="utf-8")
    print("Colonnes de RDV.csv:", rdv_data.columns)

    if 'REF' not in rdv_data.columns:
        raise ValueError("La colonne 'REF' est absente de RDV.csv")

    # Reconstruire Date_RDV au format français si nécessaire
    rebuild_date_rdv(rdv_data)

    # Convertir les dates en format datetime pour une comparaison facile
    rdv_data['Date_RDV'] = pd.to_datetime(rdv_data['Date_RDV'], errors='coerce')

    # Filtrer les rendez-vous passés
    today = pd.to_datetime(datetime.now().date())  # Aujourd'hui au format datetime
    passed_appointments = rdv_data[rdv_data['Date_RDV'] < today]

    if not passed_appointments.empty:
        # Sauvegarder les rendez-vous passés dans le fichier de purge
        passed_appointments.to_csv(file_purge_rdv, index=False, mode='w', encoding='utf-8')
        print(f"{len(passed_appointments)} rendez-vous passés ont été enregistrés dans Purge_RDV.csv.")

        # Supprimer les lignes copiées dans RDV.csv
        rdv_data = rdv_data[rdv_data['Date_RDV'] >= today]
        rdv_data.to_csv(file_path_rdv, index=False, encoding='utf-8')
        print(f"Les rendez-vous passés ont été supprimés de RDV.csv.")
    else:
        print("Aucun rendez-vous passé à sauvegarder.")

except Exception as e:
    print(f"Erreur lors de la manipulation des données RDV : {e}")

# Initialiser la session state
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
if "selected_time" not in st.session_state:
    st.session_state.selected_time = None
if "active_page" not in st.session_state:
    st.session_state.active_page = "Consultation"

# Liste des jours fériés en France pour l'année en cours
def get_french_holidays(year):
    return [
        date(year, 1, 1),  # Jour de l'an
        date(year, 4, 10),  # Lundi de Pâques (exemple pour 2023, ajustez chaque année)
        date(year, 5, 1),  # Fête du Travail
        date(year, 5, 8),  # Victoire 1945
        date(year, 5, 18),  # Ascension (exemple pour 2023, ajustez chaque année)
        date(year, 5, 29),  # Lundi de Pentecôte (exemple pour 2023, ajustez chaque année)
        date(year, 7, 14),  # Fête nationale
        date(year, 8, 15),  # Assomption
        date(year, 11, 1),  # Toussaint
        date(year, 11, 11),  # Armistice 1918
        date(year, 12, 25)  # Noël
    ]

# Obtenez les jours fériés pour l'année en cours
current_year_holidays = get_french_holidays(date.today().year)

# Fonction pour reconstruire Date_RDV si nécessaire
def rebuild_date_rdv(df):
    if {'JRDV', 'MRDV', 'ARDV'}.issubset(df.columns):
        mask_nan_dates = df['Date_RDV'].isna()
        if mask_nan_dates.any():
            df.loc[mask_nan_dates, 'Date_RDV'] = pd.to_datetime(
                df.loc[mask_nan_dates, ['ARDV', 'MRDV', 'JRDV']].rename(
                    columns={'ARDV': 'year', 'MRDV': 'month', 'JRDV': 'day'}),
                errors='coerce'
            ).dt.strftime('%d/%m/%Y')

# Fonction pour vérifier la cohérence des données entre les deux fichiers
def check_data_consistency(patients_df, rdv_df):
    # Vérifier que tous les REF dans rdv_df existent dans patients_df
    rdv_refs = rdv_df['REF'].unique()
    patient_refs = patients_df['REF'].unique()
    missing_refs = set(rdv_refs) - set(patient_refs)

    if missing_refs:
        st.error("Les REF suivants dans RDV.csv n'existent pas dans BDD_Michka.csv:")
        for ref in missing_refs:
            st.error(f"REF {ref}")

# ✅ Initialisation des variables de session
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'page' not in st.session_state:
    st.session_state.page = "Menu"  # Initialiser la page à "Menu"
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'patients_data' not in st.session_state:
    try:
        # Chargement des données des patients
        patients_data = pd.read_csv(file_path_patients, sep=',', encoding="utf-8")
        print("Colonnes de BDD_Michka.csv:", patients_data.columns)

        if 'REF' not in patients_data.columns:
            raise ValueError("La colonne 'REF' est absente de BDD_Michka.csv")

        # Vérifier le type de la colonne REF
        patients_data['REF'] = patients_data['REF'].astype(int)

        # Chargement des données de rendez-vous
        rdv_data = pd.read_csv(file_path_rdv, sep=',', encoding="utf-8")
        print("Colonnes de RDV.csv:", rdv_data.columns)

        if 'REF' not in rdv_data.columns:
            raise ValueError("La colonne 'REF' est absente de RDV.csv")

        # Vérifier le type de la colonne REF
        rdv_data['REF'] = rdv_data['REF'].astype(int)

        # Vérifier la cohérence des données
        check_data_consistency(patients_data, rdv_data)

        # Reconstruire Date_RDV si nécessaire
        rebuild_date_rdv(rdv_data)

        # Convertir Heure_RDV en format lisible
        def format_heure(x):
            try:
                heure = int(x.split(':')[0])  # Assurez-vous que x est un entier
                return f"{heure:02d}:00"
            except ValueError:
                return x  # Retourner la valeur originale si elle ne peut pas être convertie

        rdv_data["Heure_RDV"] = rdv_data["Heure_RDV"].apply(format_heure)

        st.session_state.patients_data = patients_data
        st.session_state.rdv_data = rdv_data

        # Debugging: Print the loaded data
        print("Patients Data:")
        print(st.session_state.patients_data.head())
        print("Rendez-vous Data:")
        print(st.session_state.rdv_data.head())

    except Exception as e:
        st.session_state.patients_data = pd.DataFrame()
        st.session_state.rdv_data = pd.DataFrame()
        st.error(f"Erreur lors du chargement des données: {e}")
        print(f"Error loading data: {e}")

# Fonction pour générer un REF unique
def generate_unique_ref():
    if not st.session_state.patients_data.empty:
        return st.session_state.patients_data['REF'].max() + 1
    else:
        return 1

# 🔐 Fonction de connexion
def connexion():
    if not st.session_state.authenticated:
        user_type = st.radio("Sélectionnez votre profil :", ('Professionnel', 'Particulier'))
        password = st.text_input("Entrez le mot de passe :", type="password")

        if st.button("Accéder"):
            if (user_type == 'Professionnel' and password == 'pro') or (
                    user_type == 'Particulier' and password == 'part'):
                st.session_state.user_type = user_type
                st.session_state.authenticated = True
                st.session_state.page = "Menu"
            else:
                st.error("Mot de passe incorrect.")
    else:
        menu_professionnel() if st.session_state.user_type == 'Professionnel' else menu_particulier()

# 🏥 Menu professionnel
def menu_professionnel():
    st.write("Bienvenue dans l'espace professionnel de Michka.")
    choix = st.sidebar.selectbox("Menu", ["Consultation", "Calendrier", "Patient"])

    # Mettre à jour la page actuelle dans la session
    st.session_state.page = choix

    if choix == "Consultation":
        consulter_patient()
    elif choix == "Calendrier":
        calendrier_rendez_vous()
    elif choix == "Patient":
        ajouter_modifier_patient()

# 📋 Fonction pour consulter un patient
def consulter_patient():
    st.subheader("Consultation d'un patient")

    df = st.session_state.patients_data
    rdv_df = st.session_state.rdv_data

    if df.empty or rdv_df.empty:
        st.warning("Aucune donnée disponible.")
        return

    # Sélectionner un patient
    selected_person = st.selectbox("Sélectionnez une personne :", df["Nom"].unique())

    # Récupérer ses informations
    person_details = df[df["Nom"] == selected_person].iloc[0]

    # 📝 Afficher les informations du patient
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Nom :** {person_details['Nom']}")
    with col2:
        st.markdown(f"**Prénom :** {person_details['Prenom']}")
    with col3:
        st.markdown(f"**Âge :** {person_details['Age']} ans")
    with col4:
        st.markdown(f"**REF :** {person_details['REF']}")

    st.markdown(f"**Niveau :** {person_details['Niveau']}")

    # 📅 Afficher tous les prochains RDV
    st.subheader("Prochains rendez-vous")
    rdv_person = rdv_df[rdv_df["Nom"] == selected_person].sort_values(by="Date_RDV")
    if not rdv_person.empty:
        rdv_list = rdv_person[["Date_RDV", "Heure_RDV"]].values.tolist()
        for i in range(0, len(rdv_list), 4):
            cols = st.columns(4)
            for j, (date_rdv, heure_rdv) in enumerate(rdv_list[i:i+4]):
                # Convertir la date en format français
                date_rdv_formatted = pd.to_datetime(date_rdv, errors='coerce').strftime('%d-%m-%Y')
                # Créer un bouton pour chaque rendez-vous
                if cols[j].button(f"{date_rdv_formatted} à {heure_rdv}"):
                    # Mettre à jour la variable de session pour afficher le calendrier
                    st.session_state.selected_date = pd.to_datetime(date_rdv, errors='coerce').date()
                    st.session_state.selected_time = heure_rdv
                    st.session_state.page = "Calendrier"
                    st.rerun()  # Utilisez st.rerun() si vous êtes sur une version plus récente
    else:
        st.markdown("**Aucun rendez-vous prévu**")

    # 📊 Génération des graphiques aléatoires
    st.subheader("Évolution de l'apprentissage")

    # 1️⃣ Histogramme des scores
    scores = np.random.randint(50, 100, 20)
    fig, ax = plt.subplots()
    sns.histplot(scores, bins=10, kde=True, ax=ax)
    ax.set_title("Distribution des scores aux exercices")
    ax.set_xlabel("Score")
    ax.set_ylabel("Fréquence")
    st.pyplot(fig)

    # 2️⃣ Courbe d'évolution des scores
    progression = np.cumsum(np.random.randint(0, 5, 10)) + 50
    dates = pd.date_range(start=date.today(), periods=10)
    fig, ax = plt.subplots()
    ax.plot(dates, progression, marker='o', linestyle='-')
    ax.set_title("Progression des scores au fil du temps")
    ax.set_xlabel("Date")
    ax.set_ylabel("Score")
    ax.grid(True)
    st.pyplot(fig)

    # 3️⃣ Diagramme en radar des compétences
    labels = ["Vocabulaire", "Fluidité", "Compréhension", "Expression", "Mémorisation"]
    stats = np.random.randint(50, 100, len(labels))
    stats = np.append(stats, stats[0])
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={"polar": True})
    ax.fill(angles, stats, color='b', alpha=0.3)
    ax.plot(angles, stats, marker='o')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title("Évaluation des compétences en langue des signes")
    st.pyplot(fig)

    # 4️⃣ Graphique en barres des performances par niveau
    niveaux = ["Débutant", "Intermédiaire", "Avancé"]
    scores_moyens = [np.random.randint(50, 70), np.random.randint(70, 85), np.random.randint(85, 100)]
    fig, ax = plt.subplots()
    sns.barplot(x=niveaux, y=scores_moyens, ax=ax, palette="viridis")
    ax.set_title("Comparaison des performances entre niveaux")
    ax.set_xlabel("Niveau")
    ax.set_ylabel("Score moyen")
    st.pyplot(fig)

# 📅 Affichage du calendrier des rendez-vous avec option de modification
def calendrier_rendez_vous():
    #st.title("Calendrier des rendez-vous")
    st.subheader("Calendrier")
    if st.session_state.selected_date and st.session_state.selected_time:
        st.write(f"Rendez-vous sélectionné : {st.session_state.selected_date.strftime('%d-%m-%Y')} à {st.session_state.selected_time}")

    rdv_df = st.session_state.rdv_data
    patients_df = st.session_state.patients_data

    if rdv_df.empty:
        st.warning("Aucun rendez-vous enregistré.")
        return

    # Initialiser date_selectionnee avec la date d'aujourd'hui ou la date sélectionnée
    date_selectionnee = st.session_state.get('selected_date', date.today())

    # Interface utilisateur pour sélectionner une date
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Choisissez une date")
    with col2:
        # Limiter la sélection de la date aux jours à partir d'aujourd'hui
        date_selectionnee = st.date_input("", date_selectionnee, min_value=date.today())
        st.session_state.selected_date = date_selectionnee

    # Vérifier si la date sélectionnée est valide avant d'utiliser weekday()
    if date_selectionnee is not None:
        if date_selectionnee.weekday() == 6 or date_selectionnee in current_year_holidays:
            st.error("Les rendez-vous ne peuvent pas être pris les dimanches ou les jours fériés.")
            return
    else:
        st.error("Veuillez sélectionner une date valide.")
        return

    # Assurez-vous que Date_RDV est bien de type datetime
    if not pd.api.types.is_datetime64_any_dtype(rdv_df["Date_RDV"]):
        rdv_df["Date_RDV"] = pd.to_datetime(rdv_df["Date_RDV"], errors='coerce')

    rdv_du_jour = rdv_df[rdv_df["Date_RDV"] == date_selectionnee.strftime('%d/%m/%Y')]

    # Définition des créneaux horaires
    horaires_disponibles = [f"{h:02d}:00" for h in range(8, 19)]
    if date_selectionnee == date.today():
        # Exclure les heures déjà passées aujourd'hui
        current_time = datetime.now().time()
        horaires_disponibles = [heure for heure in horaires_disponibles if time.fromisoformat(heure) > current_time]

    horaires_pris = set(rdv_du_jour["Heure_RDV"].dropna().astype(str))
    total_creneaux = len(horaires_disponibles)
    creneaux_restants = total_creneaux - len(horaires_pris)

    # Déterminer la couleur de la journée
    if creneaux_restants == 0:
        couleur_journee, texte_journee = "red", "Complet"
    elif creneaux_restants < total_creneaux:
        couleur_journee, texte_journee = "orange", f"Partiellement pris ({creneaux_restants} créneaux restants)"
    else:
        couleur_journee, texte_journee = "green", "Tous les créneaux sont libres"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("Disponibilité")
    with col2:
        st.markdown(
            f"<div style='background-color:{couleur_journee}; padding:5px; margin:5px; border-radius:5px; color:white; text-align:center;'>"
            f"{date_selectionnee.strftime('%d-%m-%Y')} - {texte_journee}</div>",
            unsafe_allow_html=True
        )

    # Affichage du calendrier
    st.write(f"### Créneaux horaires pour le {date_selectionnee.strftime('%d-%m-%Y')}")
    for heure in horaires_disponibles:
        if heure in horaires_pris:
            patient = rdv_du_jour[rdv_du_jour["Heure_RDV"].astype(str) == heure].iloc[0]
            texte = f"Pris ({patient['Prenom']} {patient['Nom']})"
            couleur = "orange"  # Créneau pris
        else:
            texte = "Libre"
            couleur = "green"  # Créneau libre

        st.markdown(
            f"<div style='background-color:{couleur}; padding:5px; margin:5px; border-radius:5px; color:white; text-align:center;'>"
            f"{heure} - {texte}</div>",
            unsafe_allow_html=True
        )

    # Sélection du patient et du rendez-vous
    col1, col2 = st.columns([1, 1])
    with col1:
        # Utiliser patients_df pour choisir un patient existant
        patient_ajout = st.selectbox("", patients_df.apply(lambda x: f"{x['Prenom']} {x['Nom']}", axis=1),
                                     key="select_patient")
        selected_patient = \
        patients_df[patients_df.apply(lambda x: f"{x['Prenom']} {x['Nom']}", axis=1) == patient_ajout].iloc[0]
    with col2:
        rdv_modifiable = rdv_du_jour[['Prenom', 'Nom', 'Heure_RDV']].dropna()
        selected_rdv = None
        if not rdv_modifiable.empty:
            selected_rdv = st.selectbox("", [f"{row['Prenom']} {row['Nom']} - {row['Heure_RDV']}" for _, row in
                                             rdv_modifiable.iterrows()], key="select_rdv")

    st.write("Nouvelle Heure")
    new_time = st.selectbox("", horaires_disponibles, key="select_new_time")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ajouter un rendez-vous", key="btn_ajouter"):
            if new_time not in horaires_pris:
                ref = selected_patient['REF']  # Utiliser le REF existant du patient sélectionné
                prenom, nom = selected_patient['Prenom'], selected_patient['Nom']

                # Convertir la date sélectionnée en jour, mois, année
                date_obj = datetime.strptime(date_selectionnee.strftime('%d/%m/%Y'), '%d/%m/%Y')
                jour_rdv = date_obj.day
                mois_rdv = date_obj.month
                annee_rdv = date_obj.year

                new_rdv = pd.DataFrame({
                    "REF": [ref],
                    "Prenom": [prenom],
                    "Nom": [nom],
                    "JRDV": [jour_rdv],
                    "MRDV": [mois_rdv],
                    "ARDV": [annee_rdv],
                    "Date_RDV": [date_selectionnee.strftime('%d/%m/%Y')],
                    "Heure_RDV": [new_time]
                })
                st.session_state.rdv_data = pd.concat([st.session_state.rdv_data, new_rdv], ignore_index=True)
                st.session_state.rdv_data.sort_values(by=["Date_RDV", "Heure_RDV"], inplace=True)
                st.session_state.rdv_data.to_csv(file_path_rdv, sep=',', index=False, encoding="utf-8")
                st.success("Rendez-vous ajouté avec succès !")
                st.rerun()
            else:
                st.error("Ce créneau horaire est déjà pris.")

    with col2:
        if selected_rdv and st.button("Modifier le rendez-vous", key="btn_modifier"):
            selected_patient = selected_rdv.split(" - ")[0].split(" ")
            if new_time not in horaires_pris:
                st.session_state.rdv_data.loc[
                    (st.session_state.rdv_data["Prenom"] == selected_patient[0]) &
                    (st.session_state.rdv_data["Nom"] == selected_patient[1]) &
                    (st.session_state.rdv_data["Date_RDV"] == date_selectionnee.strftime(
                        '%d/%m/%Y')), "Heure_RDV"] = new_time
                st.session_state.rdv_data.sort_values(by=["Date_RDV", "Heure_RDV"], inplace=True)
                st.session_state.rdv_data.to_csv(file_path_rdv, sep=',', index=False, encoding="utf-8")
                st.success("Rendez-vous mis à jour avec succès !")
                st.rerun()
            else:
                st.error("Ce créneau horaire est déjà pris.")

    with col3:
        if selected_rdv and st.button("Supprimer le rendez-vous", key="btn_supprimer"):
            selected_patient = selected_rdv.split(" - ")[0].split(" ")
            st.session_state.rdv_data = st.session_state.rdv_data[~(
                    (st.session_state.rdv_data["Prenom"] == selected_patient[0]) &
                    (st.session_state.rdv_data["Nom"] == selected_patient[1]) &
                    (st.session_state.rdv_data["Date_RDV"] == date_selectionnee.strftime('%d/%m/%Y')) &
                    (st.session_state.rdv_data["Heure_RDV"] == selected_rdv.split(" - ")[1])
            )]
            st.session_state.rdv_data.sort_values(by=["Date_RDV", "Heure_RDV"], inplace=True)
            st.session_state.rdv_data.to_csv(file_path_rdv, sep=',', index=False, encoding="utf-8")
            st.success("Rendez-vous supprimé avec succès !")
            st.rerun()


# ➕ Fonction pour ajouter un patient
def ajouter_modifier_patient():
    st.subheader("Ajout/Modification d'un patient")

    # Sélectionner une action
    action = st.radio("Choisissez une action :", ("Ajouter", "Modifier", "Supprimer"))

    if action == "Ajouter":
        # Utilisation des colonnes pour organiser les champs de saisie
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nom = st.text_input("Nom").strip().upper()
        with col2:
            prenom = st.text_input("Prénom").strip().capitalize()
        with col3:
            age = st.number_input("Âge", min_value=2, max_value=100, step=1)
        with col4:
            genre = st.selectbox("Genre", ["M", "F"])

        col1, col2, col3 = st.columns(3)
        with col1:
            niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"])
        with col2:
            cat = st.selectbox("Catégorie", ['Bebe' 'Enfant' 'Adolescent' 'Adulte' 'Avancé'])
        with col3:
            date_pc = st.date_input("Date de Prise en Charge", min_value=date.today())


        # Vérification et ajout/modification
        if st.button("Ajouter"):
            ref = generate_unique_ref()  # Générer un REF unique
            new_patient = pd.DataFrame([{
                "REF": ref,
                "Nom": nom, "Prenom": prenom, "Age": age, "Genre": genre, "Cat": cat,
                "Niveau": niveau, "JPC": date_pc.day, "MPC": date_pc.month, "APC": date_pc.year,
                "Date PC": date_pc.strftime('%d/%m/%Y'), "Date Fin": None
            }])

            st.session_state.patients_data = pd.concat([st.session_state.patients_data, new_patient], ignore_index=True)
            st.session_state.patients_data.to_csv(file_path_patients, index=False)

            st.success(f"Patient {prenom} {nom} ajouté avec succès !")

    elif action == "Modifier":
        # Code pour modifier un patient

        selected_patient = st.selectbox("Sélectionnez un patient à modifier :",st.session_state.patients_data.apply(lambda x: f"{x['Prenom']} {x['Nom']}", axis=1))
        patient_data = st.session_state.patients_data[st.session_state.patients_data.apply(lambda x: f"{x['Prenom']} {x['Nom']}", axis=1) == selected_patient].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nom = st.text_input("Nom", value=patient_data["Nom"]).strip().upper()
        with col2:
            prenom = st.text_input("Prénom", value=patient_data["Prenom"]).strip().capitalize()
        with col3:
            age = st.number_input("Âge", min_value=2, max_value=100, step=1, value=patient_data["Age"])
        with col4:
            genre = st.selectbox("Genre", ["M", "F"], index=["M", "F"].index(patient_data["Genre"]))

        col1, col2, col3 = st.columns(3)
        with col1:
            niveau = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"],
                              index=["Débutant", "Intermédiaire", "Avancé"].index(patient_data["Niveau"]))
        with col2:
            categories = ["Bebe", "Enfant", "Adolescent", "Adulte", "Avancé"]
            if patient_data["Cat"] not in categories:
                categories.append(patient_data["Cat"])  # Ajouter la catégorie si elle est manquante

            cat = st.selectbox("Catégorie", categories,
                               index=categories.index(patient_data["Cat"]))
        with col3:
            date_pc = st.date_input("Date de Prise en Charge", value=pd.to_datetime(patient_data["Date PC"]))

        if st.button("Modifier"):
            st.session_state.patients_data.loc[st.session_state.patients_data["REF"] == patient_data["REF"],
                                               ["Nom", "Prenom", "Age", "Genre", "Cat", "Niveau", "JPC", "MPC", "APC", "Date PC"]] = \
                [nom, prenom, age, genre, cat, niveau, date_pc.day, date_pc.month, date_pc.year, date_pc.strftime('%d/%m/%Y')]

            st.session_state.patients_data.to_csv(file_path_patients, index=False)
            st.success(f"Patient {prenom} {nom} modifié avec succès !")

    elif action == "Supprimer":
        # Sélectionner un patient à supprimer
        selected_patient = st.selectbox("Sélectionnez un patient à supprimer :",
                                        st.session_state.patients_data.apply(lambda x: f"{x['Prenom']} {x['Nom']}", axis=1))

        if st.button("Supprimer"):
            st.session_state.patients_data = st.session_state.patients_data[st.session_state.patients_data.apply(
                lambda x: f"{x['Prenom']} {x['Nom']}", axis=1) != selected_patient]

            st.session_state.patients_data.to_csv(file_path_patients, index=False)
            st.success(f"Patient {selected_patient} supprimé avec succès !")
#-----------------------------------------------------------------------------------------------------------------------



# Démarrer l'application
connexion()
