
import streamlit as st
import pandas as pd
import openai
from datetime import datetime
import uuid

st.set_page_config(page_title="Ambre", layout="centered")

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 15px !important;
    }
    .block-container { padding: 1rem; }
    </style>
""", unsafe_allow_html=True)

client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# Chargement CSV
DATA_PATH = "data.csv"
try:
    df = pd.read_csv(DATA_PATH)
except:
    df = pd.DataFrame(columns=["user_id", "name", "source", "notes", "score", "message", "sender", "timestamp"])

# Navigation
page = st.sidebar.radio("Navigation", ["Accueil", "Créer utilisateur", "Utilisateurs"])

# Enregistrement
def save_data():
    df.to_csv(DATA_PATH, index=False)

# Accueil
if page == "Accueil":
    st.title("Bienvenue dans Ambre 💬")
    st.markdown("Gérez vos conversations, profils, historiques et PPV depuis votre téléphone !")

# Créer utilisateur
elif page == "Créer utilisateur":
    st.title("Créer un nouvel utilisateur")
    name = st.text_input("Prénom ou pseudo")
    source = st.selectbox("Provenance", ["Instagram", "Telegram", "MYM", "Uncove", "Twitter", "Threads", "OnlyFans", "Snapchat"])
    notes = st.text_area("Notes", height=100)
    if st.button("Créer"):
        new_id = str(uuid.uuid4())[:8]
        new_user = {
            "user_id": new_id,
            "name": name,
            "source": source,
            "notes": notes,
            "score": 0,
            "message": "",
            "sender": "system",
            "timestamp": datetime.now().isoformat()
        }
        df.loc[len(df)] = new_user
        save_data()
        st.success(f"Utilisateur {name} ajouté ✅")

# Utilisateurs
elif page == "Utilisateurs":
    st.title("Utilisateurs")
    users = df.groupby("user_id").first().reset_index()
    if len(users) == 0:
        st.info("Aucun utilisateur.")
    else:
        user_selected = st.selectbox("Choisir un utilisateur", users["name"])
        current_id = users[users["name"] == user_selected]["user_id"].values[0]
        user_data = df[df["user_id"] == current_id]
        st.markdown(f"**Provenance :** {user_data['source'].iloc[0]}")
        st.markdown(f"**Notes :** {user_data['notes'].iloc[0]}")
        st.markdown(f"**Score :** {user_data['score'].iloc[0]}")

        # Chat
        st.markdown("---")
        st.subheader("💬 Chat")
        for _, row in user_data.iterrows():
            who = "👤" if row["sender"] == "user" else "💬 Ambre"
            st.markdown(f"**{who}** : {row['message']}")

        msg = st.text_input("Message")
        if st.button("Envoyer"):
            df.loc[len(df)] = {
                "user_id": current_id,
                "name": user_selected,
                "source": user_data['source'].iloc[0],
                "notes": user_data['notes'].iloc[0],
                "score": user_data['score'].iloc[0],
                "message": msg,
                "sender": "user",
                "timestamp": datetime.now().isoformat()
            }

            prompt = f"Tu es Ambre, modèle douce et coquine sur MYM. Réponds avec des emojis en 3 phrases max au message suivant : {msg}"

            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": msg}
                ]
            )
            reply = completion.choices[0].message.content.strip()
            df.loc[len(df)] = {
                "user_id": current_id,
                "name": user_selected,
                "source": user_data['source'].iloc[0],
                "notes": user_data['notes'].iloc[0],
                "score": user_data['score'].iloc[0],
                "message": reply,
                "sender": "ambre",
                "timestamp": datetime.now().isoformat()
            }
            save_data()
            st.success("Réponse envoyée ✅")
