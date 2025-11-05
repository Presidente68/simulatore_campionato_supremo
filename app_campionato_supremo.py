"""
CAMPIONATO SUPREMO - VERSIONE OTTIMIZZATA PER MOBILE
Streamlit App con dropdown per classifica e sistema tracking stato
"""

import streamlit as st
import pandas as pd
import numpy as np
import math

# ==================== CONFIGURAZIONE PAGINA ====================

st.set_page_config(
    page_title="Campionato Supremo",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PERSONALIZZATO ====================

st.markdown("""
<style>
/* Pulsante ROSSO - Calcolo Necessario */
button[kind="primary"]:has(> div:first-child:contains("⚠️")) {
    background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%) !important;
    border: 2px solid #991b1b !important;
    animation: pulse 2s infinite;
    font-weight: 600;
}

/* Pulsante VERDE - Già Calcolato */
button[kind="primary"]:has(> div:first-child:contains("✅")) {
    background: linear-gradient(90deg, #16a34a 0%, #22c55e 100%) !important;
    border: 2px solid #15803d !important;
    opacity: 0.7;
    cursor: not-allowed;
}

/* Animazione pulse per attirare attenzione */
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.02); }
}

/* Migliora visualizzazione dropdown su mobile */
@media (max-width: 640px) {
    .stSelectbox {
        font-size: 14px;
    }
    label {
        font-size: 13px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==================== COSTANTI ====================

# Liste squadre disponibili
TUTTE_SQUADRE = [
    "Napoli", "Inter", "Juventus", "Milan", "Roma", 
    "Fiorentina", "Atalanta", "Como", "Lazio", "Bologna",
    "Torino", "Udinese", "Genoa", "Cagliari", "Cremonese",
    "Parma", "Sassuolo", "Lecce", "Verona", "Pisa"
]

# Partecipanti
PARTECIPANTI = ["Andrea", "Carlo", "Francesco", "Giuseppe", "Luca", "Marco"]

# Fogli giocatori
FOGLI_GIOCATORI = [f"Giocatori_{i}" for i in range(1, 6)]

# Costanti calcolo
K_FACTOR = 25
SOGLIA_GOL_CONTROCORRENTE = 5
SOGLIA_POSIZIONE_CONTROCORRENTE = 4

# ==================== INIZIALIZZAZIONE SESSION STATE ====================

def inizializza_session_state():
    """Inizializza tutte le variabili di stato necessarie"""
    
    # Classifica
    if 'classifica_list' not in st.session_state:
        st.session_state.classifica_list = [None] * 20
    if 'classifica_calcolata' not in st.session_state:
        st.session_state.classifica_calcolata = False
    if 'classifica_modificata' not in st.session_state:
        st.session_state.classifica_modificata = False
    
    # Gironi (5 gironi)
    for i in range(1, 6):
        if f'girone{i}_data' not in st.session_state:
            st.session_state[f'girone{i}_data'] = {}
        if f'girone{i}_calcolato' not in st.session_state:
            st.session_state[f'girone{i}_calcolato'] = False
        if f'girone{i}_modificato' not in st.session_state:
            st.session_state[f'girone{i}_modificato'] = False
    
    # Generale
    if 'generale_calcolata' not in st.session_state:
        st.session_state.generale_calcolata = False
    if 'risultati_parziali' not in st.session_state:
        st.session_state.risultati_parziali = {}

# ==================== FUNZIONI CALCOLO PUNTEGGI ====================

def calcola_punteggio_giocatore(pronosticati, reali):
    """Calcola punteggio per un giocatore"""
    if pd.isna(reali) or reali < 3:
        return 0
    errore = abs(pronosticati - reali)
    malus = errore ** 2
    punteggio = max(0, reali - malus)
    return punteggio

def calcola_punteggio_base_squadra(prevista, reale):
    """Calcola punteggio base per una squadra"""
    errore = abs(prevista - reale)
    punteggio = max(0, 10 - (errore ** 2))
    return punteggio

# ==================== FUNZIONI UI ====================

def verifica_classifica_completa():
    """Verifica se tutte le 20 squadre sono state selezionate"""
    return all(sq is not None and sq != "--- Seleziona ---" for sq in st.session_state.classifica_list)

def get_squadre_disponibili(posizione):
    """Restituisce le squadre ancora disponibili per una data posizione"""
    squadre_usate = [
        st.session_state.classifica_list[i] 
        for i in range(20) 
        if i != posizione and st.session_state.classifica_list[i] not in [None, "--- Seleziona ---"]
    ]
    return [sq for sq in TUTTE_SQUADRE if sq not in squadre_usate]

def renderizza_pulsante_calcola(label, is_calcolato, is_modificato, help_text):
    """Renderizza un pulsante calcola con colore appropriato"""
    needs_calc = not is_calcolato or is_modificato
    
    if needs_calc:
        icona = "⚠️"
        testo = f"{icona} {label}"
        disabled = False
        help_msg = help_text + " - Dati modificati o mai calcolati"
    else:
        icona = "✅"
        testo = f"{icona} {label} (Aggiornato)"
        disabled = True
        help_msg = "Già calcolato e aggiornato"
    
    return st.button(
        testo,
        type="primary",
        disabled=disabled,
        help=help_msg,
        use_container_width=True
    )

# ==================== PAGINA DASHBOARD ====================

def pagina_dashboard():
    """Pagina principale dashboard"""
    st.title("🏆 Campionato Supremo")
    st.markdown("---")
    
    st.markdown("""
    ## Benvenuto nel Campionato Supremo! ⚽
    
    Questa applicazione ti permette di gestire e calcolare i punteggi del campionato.
    
    ### 📋 Sezioni Disponibili:
    
    1. **Classifica Squadre** - Inserisci l'ordine finale delle squadre
    2. **Gironi 1-5** - Inserisci i gol segnati dai giocatori
    3. **Classifica Generale** - Visualizza la classifica finale e le statistiche
    
    ### 🎯 Come Usare l'App:
    
    1. Vai su **Classifica Squadre** e seleziona le squadre nei dropdown
    2. Vai sui **Gironi** e inserisci i gol di ogni giocatore
    3. Clicca **CALCOLA** in ogni sezione (il pulsante diventa verde quando fatto)
    4. Vai su **Classifica Generale** per vedere i risultati finali
    
    ### 🔴 🟢 Sistema Semaforo:
    
    - **Pulsante ROSSO con ⚠️** = Devi calcolare (dati nuovi o modificati)
    - **Pulsante VERDE con ✅** = Già calcolato e aggiornato
    
    **Inizia dalla Classifica Squadre!** 👈
    """)
    
    # Mostra stato generale nella sidebar
    with st.sidebar:
        st.markdown("### 📊 Stato Sezioni")
        
        # Classifica
        if st.session_state.classifica_calcolata and not st.session_state.classifica_modificata:
            st.success("✅ Classifica")
        else:
            st.warning("⚠️ Classifica")
        
        # Gironi
        for i in range(1, 6):
            if st.session_state[f'girone{i}_calcolato'] and not st.session_state[f'girone{i}_modificato']:
                st.success(f"✅ Girone {i}")
            else:
                st.warning(f"⚠️ Girone {i}")
        
        # Generale
        if st.session_state.generale_calcolata:
            st.success("✅ Generale")
        else:
            st.warning("⚠️ Generale")

# ==================== PAGINA CLASSIFICA ====================

def pagina_classifica():
    """Pagina per l'inserimento della classifica"""
    st.title("📋 Classifica Squadre")
    st.markdown("---")
    
    st.info("💡 **Seleziona le squadre nei dropdown** - Le squadre già usate non appaiono nelle posizioni successive")
    
    # Colonne per i pulsanti principali
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔄 Reset Classifica", help="Cancella tutte le selezioni"):
            st.session_state.classifica_list = [None] * 20
            st.session_state.classifica_calcolata = False
            st.session_state.classifica_modificata = False
            st.session_state.generale_calcolata = False
            st.rerun()
    
    st.markdown("### Seleziona le squadre in ordine")
    
    # Rendering dei 20 dropdown
    for i in range(20):
        squadre_disp = get_squadre_disponibili(i)
        opzioni = ["--- Seleziona ---"] + squadre_disp
        
        # Trova l'indice corrente
        valore_corrente = st.session_state.classifica_list[i]
        if valore_corrente in opzioni:
            indice = opzioni.index(valore_corrente)
        else:
            indice = 0
        
        # Selectbox
        nuova_squadra = st.selectbox(
            f"Posizione {i+1}",
            options=opzioni,
            index=indice,
            key=f"pos_{i}",
            help=f"Seleziona la squadra che finirà {i+1}ª"
        )
        
        # Detect cambiamento
        if nuova_squadra != valore_corrente:
            st.session_state.classifica_list[i] = nuova_squadra
            if nuova_squadra != "--- Seleziona ---":
                st.session_state.classifica_modificata = True
                st.session_state.generale_calcolata = False
    
    # Verifica completezza
    completa = verifica_classifica_completa()
    
    if completa:
        st.success("✅ Tutte le 20 squadre sono state inserite!")
    else:
        squadre_mancanti = 20 - sum(1 for sq in st.session_state.classifica_list if sq not in [None, "--- Seleziona ---"])
        st.warning(f"⚠️ Mancano ancora {squadre_mancanti} squadre da inserire")
    
    st.markdown("---")
    
    # Pulsante Calcola
    with col2:
        simula = renderizza_pulsante_calcola(
            "CALCOLA CLASSIFICA",
            st.session_state.classifica_calcolata,
            st.session_state.classifica_modificata,
            "Calcola i punteggi della classifica"
        )
    
    if simula and completa:
        with st.spinner("🔄 Calcolo in corso..."):
            # TODO: Implementare logica calcolo classifica completa
            # Per ora simulazione base
            st.session_state.classifica_calcolata = True
            st.session_state.classifica_modificata = False
            st.success("✅ Classifica calcolata!")
            st.balloons()

# ==================== PAGINA GIRONE ====================

def pagina_girone(num_girone):
    """Pagina per l'inserimento gol di un girone"""
    st.title(f"⚽ Girone {num_girone}")
    st.markdown("---")
    
    st.info(f"💡 **Inserisci i gol** segnati da ogni giocatore del Girone {num_girone}")
    
    # Esempio di giocatori (sostituisci con dati reali)
    giocatori_esempio = [f"Giocatore {i}" for i in range(1, 21)]
    
    # Colonne per organizzazione
    col1, col2 = st.columns(2)
    
    for idx, giocatore in enumerate(giocatori_esempio):
        with col1 if idx < 10 else col2:
            gol = st.number_input(
                giocatore,
                min_value=0,
                max_value=50,
                value=st.session_state[f'girone{num_girone}_data'].get(giocatore, 0),
                key=f"girone{num_girone}_{giocatore}",
                help=f"Gol segnati da {giocatore}"
            )
            
            # Detect cambiamento
            if gol != st.session_state[f'girone{num_girone}_data'].get(giocatore, 0):
                st.session_state[f'girone{num_girone}_data'][giocatore] = gol
                st.session_state[f'girone{num_girone}_modificato'] = True
                st.session_state.generale_calcolata = False
    
    st.markdown("---")
    
    # Pulsante Calcola
    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn2:
        calcola = renderizza_pulsante_calcola(
            f"CALCOLA GIRONE {num_girone}",
            st.session_state[f'girone{num_girone}_calcolato'],
            st.session_state[f'girone{num_girone}_modificato'],
            f"Calcola i punteggi del Girone {num_girone}"
        )
    
    if calcola:
        with st.spinner("🔄 Calcolo in corso..."):
            # TODO: Implementare logica calcolo girone
            st.session_state[f'girone{num_girone}_calcolato'] = True
            st.session_state[f'girone{num_girone}_modificato'] = False
            st.success(f"✅ Girone {num_girone} calcolato!")

# ==================== PAGINA CLASSIFICA GENERALE ====================

def pagina_generale():
    """Pagina classifica generale e statistiche"""
    st.title("📊 Classifica Generale")
    st.markdown("---")
    
    # Verifica se tutti i parziali sono calcolati
    tutti_ok = (
        st.session_state.classifica_calcolata and 
        not st.session_state.classifica_modificata and
        all(st.session_state[f'girone{i}_calcolato'] and not st.session_state[f'girone{i}_modificato'] for i in range(1, 6))
    )
    
    if not tutti_ok:
        st.warning("⚠️ **Attenzione**: Alcuni calcoli parziali non sono aggiornati!")
        st.markdown("### Stato Calcoli:")
        
        # Mostra stato dettagliato
        if not st.session_state.classifica_calcolata or st.session_state.classifica_modificata:
            st.error("❌ Classifica Squadre non calcolata o modificata")
        else:
            st.success("✅ Classifica Squadre aggiornata")
        
        for i in range(1, 6):
            if not st.session_state[f'girone{i}_calcolato'] or st.session_state[f'girone{i}_modificato']:
                st.error(f"❌ Girone {i} non calcolato o modificato")
            else:
                st.success(f"✅ Girone {i} aggiornato")
    
    st.markdown("---")
    
    # Pulsante Calcola Generale
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        calcola_gen = renderizza_pulsante_calcola(
            "CALCOLA CLASSIFICA GENERALE",
            st.session_state.generale_calcolata,
            not tutti_ok,
            "Calcola la classifica generale finale"
        )
    
    if calcola_gen and tutti_ok:
        with st.spinner("🔄 Calcolo classifica generale..."):
            # TODO: Implementare calcolo generale completo
            st.session_state.generale_calcolata = True
            st.success("✅ Classifica Generale calcolata!")
            st.balloons()
    
    # Mostra risultati se disponibili
    if st.session_state.generale_calcolata and 'Classifica_Finale' in st.session_state.risultati_parziali:
        st.markdown("### 🏆 Classifica Finale")
        st.dataframe(
            st.session_state.risultati_parziali['Classifica_Finale'],
            use_container_width=True,
            hide_index=True
        )

# ==================== MAIN ====================

def main():
    """Funzione principale dell'app"""
    
    # Inizializza session state
    inizializza_session_state()
    
    # Sidebar navigazione
    with st.sidebar:
        st.title("🏆 Campionato Supremo")
        st.markdown("---")
        
        pagina = st.radio(
            "📍 Navigazione",
            [
                "📊 Dashboard",
                "📋 Classifica Squadre",
                "⚽ Girone 1",
                "⚽ Girone 2",
                "⚽ Girone 3",
                "⚽ Girone 4",
                "⚽ Girone 5",
                "📈 Classifica Generale"
            ]
        )
    
    # Routing pagine
    if pagina == "📊 Dashboard":
        pagina_dashboard()
    elif pagina == "📋 Classifica Squadre":
        pagina_classifica()
    elif pagina.startswith("⚽ Girone"):
        num = int(pagina.split()[-1])
        pagina_girone(num)
    elif pagina == "📈 Classifica Generale":
        pagina_generale()

if __name__ == "__main__":
    main()

