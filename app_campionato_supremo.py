"""
CAMPIONATO SUPREMO - VERSIONE CORRETTA BUG
Fix: Doppia colonna, pulsante verde immediato, tabella persistente
"""

import streamlit as st
import pandas as pd
import numpy as np
import math
import os

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

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.02); }
}

@media (max-width: 640px) {
    .stSelectbox { font-size: 14px; }
    label { font-size: 13px !important; }
}
</style>
""", unsafe_allow_html=True)

# ==================== COSTANTI ====================

INPUT_FILE = 'RiepilogoCampionatoSupremo.xlsx'
K_FACTOR = 25
SOGLIA_GOL_CONTROCORRENTE = 5
SOGLIA_POSIZIONE_CONTROCORRENTE = 4

TUTTE_SQUADRE = [
    "Napoli", "Inter", "Juventus", "Milan", "Roma", "Fiorentina", 
    "Atalanta", "Como", "Lazio", "Bologna", "Torino", "Udinese", 
    "Genoa", "Cagliari", "Cremonese", "Parma", "Sassuolo", 
    "Lecce", "Verona", "Pisa"
]

# ==================== CARICAMENTO DATI EXCEL ====================

@st.cache_data
def carica_dati_excel():
    """Carica tutti i dati dal file Excel"""
    if not os.path.exists(INPUT_FILE):
        st.error(f"❌ File {INPUT_FILE} non trovato!")
        return None, None, None
    
    try:
        # Carica classifica
        df_class = pd.read_excel(INPUT_FILE, sheet_name="Classifica")
        partecipanti = [col for col in df_class.columns if col not in ['Pos', 'REALE', 'REALI', 'Posizione']]
        
        # Crea dizionario previsioni classifica
        prev_class = {}
        for idx, row in df_class.iterrows():
            pos = idx + 1
            prev_class[pos] = {part: row[part] for part in partecipanti}
        
        # Carica tutti i gironi
        gironi_data = {}
        for i in range(1, 6):
            df_girone = pd.read_excel(INPUT_FILE, sheet_name=f"Giocatori_{i}")
            gironi_data[i] = {
                'giocatori': df_girone['Giocatore'].tolist(),
                'reali': df_girone['REALI'].tolist(),
                'previsioni': {part: df_girone[part].tolist() for part in partecipanti}
            }
        
        return partecipanti, prev_class, gironi_data
    
    except Exception as e:
        st.error(f"❌ Errore nel caricamento: {str(e)}")
        return None, None, None

# ==================== FUNZIONI CALCOLO ====================

def calcola_punteggio_giocatore(pronosticati, reali):
    """Calcola punteggio per un giocatore - NON PUÒ ESSERE NEGATIVO"""
    if pd.isna(reali) or reali < 3:
        return 0
    errore = abs(pronosticati - reali)
    malus = errore ** 2
    punteggio = reali - malus
    return max(0, punteggio)  # Garantisce che il punteggio non sia mai negativo

def calcola_punteggio_base_squadra(prevista, reale):
    """Calcola punteggio base squadra"""
    errore = abs(prevista - reale)
    return max(0, 10 - (errore ** 2))

def simula_classifica_completa(classifica_list, previsioni_class, partecipanti):
    """Calcola punteggi classifica - RITORNA DATAFRAME CON ASSOLUTI E SUPREMI"""
    mappa_reali = {sq: i+1 for i, sq in enumerate(classifica_list)}
    mappe_prev = {}
    
    # Crea mappe previsioni
    for part in partecipanti:
        mappa = {}
        for sq in classifica_list:
            for pos, prev_dict in previsioni_class.items():
                if prev_dict.get(part) == sq:
                    mappa[sq] = pos
                    break
        mappe_prev[part] = mappa
    
    # Calcola punteggi
    punti_class = {}
    for part in partecipanti:
        tot = bonus = cc = 0
        
        for sq in classifica_list:
            reale = mappa_reali[sq]
            prev = mappe_prev[part].get(sq, 99)
            err = abs(prev - reale)
            
            # Punteggio base
            tot += calcola_punteggio_base_squadra(prev, reale)
            
            # Bonus posizioni strategiche
            if err == 0:
                if reale == 1:
                    bonus += 10
                elif 2 <= reale <= 4:
                    bonus += 3
                elif 5 <= reale <= 6:
                    bonus += 2
                elif 18 <= reale <= 20:
                    bonus += 4
            
            # Controcorrente
            altri = [mappe_prev[p].get(sq, 99) for p in partecipanti if p != part]
            if altri:
                pmc = np.mean(altri)
                if abs(prev - pmc) >= SOGLIA_POSIZIONE_CONTROCORRENTE:
                    if err == 0:
                        cc += 5
                    elif err == 1:
                        cc += 3
                    elif err > 2 and err > abs(round(pmc) - reale):
                        cc -= 5
        
        punti_class[part] = tot + bonus + cc
    
    # Bonus Oracolo
    if punti_class:
        max_p = max(punti_class.values())
        orac = [p for p, pt in punti_class.items() if pt == max_p]
        if orac:
            bo = math.ceil(10 / len(orac))
            for o in orac:
                punti_class[o] += bo
    
    # Crea DataFrame con Assoluti e Supremi
    df_ris = pd.DataFrame(list(punti_class.items()), columns=['Partecipante', 'Assoluti'])
    df_ris = df_ris.sort_values('Assoluti', ascending=False).reset_index(drop=True)
    
    # Calcola Supremi
    max_ass = df_ris['Assoluti'].max()
    if max_ass > 0:
        df_ris['Supremi'] = ((df_ris['Assoluti'] / max_ass) * K_FACTOR).round().astype(int)
    else:
        df_ris['Supremi'] = 0
    
    return df_ris

def simula_girone_completo(girone_data, gol_inseriti, partecipanti):
    """Calcola punteggi girone - RITORNA DATAFRAME CON ASSOLUTI E SUPREMI"""
    giocatori = girone_data['giocatori']
    reali = [gol_inseriti.get(gioc, 0) for gioc in giocatori]
    
    punti_girone = {}
    for part in partecipanti:
        tot = bonus = cc = 0
        previsioni_part = girone_data['previsioni'][part]
        
        for i, giocatore in enumerate(giocatori):
            prev = previsioni_part[i]
            real = reali[i]
            
            # Punteggio base
            punteggio_singolo = calcola_punteggio_giocatore(prev, real)
            tot += punteggio_singolo
            
            # Bonus capocannoniere
            if real == max(reali) and real >= 3:
                if prev == max(previsioni_part):
                    bonus += 10
            
            # Controcorrente
            altri_prev = [girone_data['previsioni'][p][i] for p in partecipanti if p != part]
            if altri_prev:
                pmc = np.mean(altri_prev)
                err = abs(prev - real)
                if abs(prev - pmc) >= SOGLIA_GOL_CONTROCORRENTE:
                    if err == 0:
                        cc += 5
                    elif err == 1:
                        cc += 3
                    elif err > 2 and err > abs(round(pmc) - real):
                        cc -= 5
        
        punti_girone[part] = tot + bonus + cc
    
    # Crea DataFrame con Assoluti e Supremi
    df_ris = pd.DataFrame(list(punti_girone.items()), columns=['Partecipante', 'Assoluti'])
    df_ris = df_ris.sort_values('Assoluti', ascending=False).reset_index(drop=True)
    
    # Calcola Supremi
    max_ass = df_ris['Assoluti'].max()
    if max_ass > 0:
        df_ris['Supremi'] = ((df_ris['Assoluti'] / max_ass) * K_FACTOR).round().astype(int)
    else:
        df_ris['Supremi'] = 0
    
    return df_ris

# ==================== SESSION STATE ====================

def inizializza_session_state(partecipanti, gironi_data):
    """Inizializza session state"""
    if 'initialized' not in st.session_state:
        st.session_state.classifica_list = [None] * 20
        st.session_state.classifica_calcolata = False
        st.session_state.classifica_modificata = False
        
        for i in range(1, 6):
            if gironi_data and i in gironi_data:
                # Inizializza con valori REALI dal file
                st.session_state[f'girone{i}_data'] = {
                    gioc: int(real) for gioc, real in 
                    zip(gironi_data[i]['giocatori'], gironi_data[i]['reali'])
                }
            else:
                st.session_state[f'girone{i}_data'] = {}
            
            st.session_state[f'girone{i}_calcolato'] = False
            st.session_state[f'girone{i}_modificato'] = False
        
        st.session_state.generale_calcolata = False
        st.session_state.risultati_parziali = {}
        st.session_state.initialized = True

# ==================== FUNZIONI UI ====================

def verifica_classifica_completa():
    """Verifica se tutte le squadre sono inserite"""
    return all(sq is not None and sq != "--- Seleziona ---" 
               for sq in st.session_state.classifica_list)

def get_squadre_disponibili(posizione):
    """Restituisce squadre disponibili"""
    usate = [st.session_state.classifica_list[i] for i in range(20) 
             if i != posizione and st.session_state.classifica_list[i] not in [None, "--- Seleziona ---"]]
    return [sq for sq in TUTTE_SQUADRE if sq not in usate]

def aggiorna_classifica(posizione):
    """Callback per aggiornare la classifica quando cambia una selezione"""
    if st.session_state.classifica_list[posizione] != "--- Seleziona ---":
        st.session_state.classifica_modificata = True
        st.session_state.generale_calcolata = False

def renderizza_pulsante_calcola(label, is_calcolato, is_modificato, help_text):
    """Renderizza pulsante con colore"""
    needs_calc = not is_calcolato or is_modificato
    icona = "⚠️" if needs_calc else "✅"
    testo = f"{icona} {label}" if needs_calc else f"{icona} {label} (Aggiornato)"
    
    return st.button(
        testo,
        type="primary",
        disabled=not needs_calc,
        help=help_text,
        use_container_width=True
    )

# ==================== PAGINE ====================

def pagina_dashboard():
    """Dashboard principale"""
    st.title("🏆 Campionato Supremo")
    st.markdown("---")
    
    st.markdown("""
    ## Benvenuto nel Campionato Supremo! ⚽
    
    ### 📋 Sezioni:
    1. **Classifica Squadre** - Seleziona ordine squadre
    2. **Gironi 1-5** - Inserisci/modifica gol giocatori
    3. **Classifica Generale** - Risultati finali
    
    ### 🎯 Come Usare:
    1. Vai su **Classifica Squadre** e seleziona nei dropdown
    2. Vai sui **Gironi** (i gol reali sono già caricati, modificali se serve)
    3. Clicca **CALCOLA** in ogni sezione (rosso → verde)
    4. Vai su **Classifica Generale** per i risultati
    
    ### 🔴 🟢 Sistema Semaforo:
    - **ROSSO ⚠️** = Devi calcolare
    - **VERDE ✅** = Già calcolato
    """)

def pagina_classifica(partecipanti, previsioni_class):
    """Pagina classifica"""
    st.title("📋 Classifica Squadre")
    st.markdown("---")
    
    st.info("💡 Seleziona le squadre - Le usate spariscono dai dropdown successivi")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Reset Classifica"):
            st.session_state.classifica_list = [None] * 20
            st.session_state.classifica_calcolata = False
            st.session_state.classifica_modificata = False
            st.rerun()
    
    st.markdown("### Seleziona le squadre")
    
    for i in range(20):
        squadre_disp = get_squadre_disponibili(i)
        opzioni = ["--- Seleziona ---"] + squadre_disp
        
        valore_corrente = st.session_state.classifica_list[i]
        indice = opzioni.index(valore_corrente) if valore_corrente in opzioni else 0
        
        st.selectbox(
            f"Posizione {i+1}",
            options=opzioni,
            index=indice,
            key=f"select_pos_{i}"
        )
        
        nuovo_valore = st.session_state[f"select_pos_{i}"]
        if nuovo_valore != valore_corrente:
            st.session_state.classifica_list[i] = nuovo_valore
            if nuovo_valore != "--- Seleziona ---":
                st.session_state.classifica_modificata = True
                st.session_state.generale_calcolata = False
    
    completa = verifica_classifica_completa()
    
    if completa:
        st.success("✅ Tutte le 20 squadre inserite!")
    else:
        mancanti = 20 - sum(1 for sq in st.session_state.classifica_list 
                           if sq not in [None, "--- Seleziona ---"])
        st.warning(f"⚠️ Mancano {mancanti} squadre")
    
    st.markdown("---")
    
    with col2:
        simula = renderizza_pulsante_calcola(
            "CALCOLA CLASSIFICA",
            st.session_state.classifica_calcolata,
            st.session_state.classifica_modificata,
            "Calcola punteggi classifica"
        )
    
    if simula and completa:
        with st.spinner("🔄 Calcolo..."):
            df_ris = simula_classifica_completa(
                st.session_state.classifica_list,
                previsioni_class,
                partecipanti
            )
            
            st.session_state.risultati_parziali['Classifica'] = df_ris
            st.session_state.classifica_calcolata = True
            st.session_state.classifica_modificata = False
        
        # FUORI dallo spinner per persistenza
        st.success("✅ Classifica calcolata!")
        st.dataframe(df_ris, use_container_width=True, hide_index=True)
        st.balloons()
    
    # Mostra risultati se già calcolati (anche senza ricalcolare)
    elif st.session_state.classifica_calcolata and 'Classifica' in st.session_state.risultati_parziali:
        st.markdown("### 📊 Risultati Classifica")
        st.dataframe(st.session_state.risultati_parziali['Classifica'], use_container_width=True, hide_index=True)

def pagina_girone(num_girone, partecipanti, gironi_data):
    """Pagina girone"""
    st.title(f"⚽ Girone {num_girone}")
    st.markdown("---")
    
    if num_girone not in gironi_data:
        st.error(f"❌ Dati Girone {num_girone} non disponibili")
        return
    
    girone = gironi_data[num_girone]
    giocatori = girone['giocatori']
    
    st.info(f"💡 I gol reali sono già caricati - Modificali se necessario")
    
    col1, col2 = st.columns(2)
    
    for idx, giocatore in enumerate(giocatori):
        default_val = st.session_state[f'girone{num_girone}_data'].get(giocatore, 0)
        
        with col1 if idx < len(giocatori)//2 else col2:
            gol = st.number_input(
                giocatore,
                min_value=0,
                max_value=50,
                value=int(default_val),
                key=f"g{num_girone}_{giocatore}"
            )
            
            if gol != default_val:
                st.session_state[f'girone{num_girone}_data'][giocatore] = gol
                st.session_state[f'girone{num_girone}_modificato'] = True
                st.session_state.generale_calcolata = False
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn2:
        calcola = renderizza_pulsante_calcola(
            f"CALCOLA GIRONE {num_girone}",
            st.session_state[f'girone{num_girone}_calcolato'],
            st.session_state[f'girone{num_girone}_modificato'],
            f"Calcola punteggi Girone {num_girone}"
        )
    
    if calcola:
        with st.spinner("🔄 Calcolo..."):
            df_ris = simula_girone_completo(
                girone,
                st.session_state[f'girone{num_girone}_data'],
                partecipanti
            )
            
            st.session_state.risultati_parziali[f'Girone{num_girone}'] = df_ris
            st.session_state[f'girone{num_girone}_calcolato'] = True
            st.session_state[f'girone{num_girone}_modificato'] = False
        
        # FUORI dallo spinner
        st.success(f"✅ Girone {num_girone} calcolato!")
        st.dataframe(df_ris, use_container_width=True, hide_index=True)
    
    # Mostra risultati se già calcolati
    elif st.session_state[f'girone{num_girone}_calcolato'] and f'Girone{num_girone}' in st.session_state.risultati_parziali:
        st.markdown(f"### 📊 Risultati Girone {num_girone}")
        st.dataframe(st.session_state.risultati_parziali[f'Girone{num_girone}'], use_container_width=True, hide_index=True)

def pagina_generale(partecipanti):
    """Classifica generale"""
    st.title("📊 Classifica Generale")
    st.markdown("---")
    
    tutti_ok = (
        st.session_state.classifica_calcolata and 
        not st.session_state.classifica_modificata and
        all(st.session_state[f'girone{i}_calcolato'] and 
            not st.session_state[f'girone{i}_modificato'] for i in range(1, 6))
    )
    
    if not tutti_ok:
        st.warning("⚠️ Alcuni calcoli non sono aggiornati!")
        if not st.session_state.classifica_calcolata or st.session_state.classifica_modificata:
            st.error("❌ Classifica Squadre")
        else:
            st.success("✅ Classifica Squadre")
        
        for i in range(1, 6):
            if not st.session_state[f'girone{i}_calcolato'] or st.session_state[f'girone{i}_modificato']:
                st.error(f"❌ Girone {i}")
            else:
                st.success(f"✅ Girone {i}")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calcola_gen = renderizza_pulsante_calcola(
            "CALCOLA CLASSIFICA GENERALE",
            st.session_state.generale_calcolata,
            not tutti_ok,
            "Calcola classifica finale"
        )
    
    if calcola_gen and tutti_ok:
        with st.spinner("🔄 Calcolo generale..."):
            # Somma tutti i punteggi ASSOLUTI parziali
            totali_assoluti = {part: 0 for part in partecipanti}
            
            for key, df in st.session_state.risultati_parziali.items():
                for _, row in df.iterrows():
                    totali_assoluti[row['Partecipante']] += row['Assoluti']
            
            # Crea DataFrame finale
            df_finale = pd.DataFrame(list(totali_assoluti.items()), columns=['Partecipante', 'Assoluti'])
            df_finale = df_finale.sort_values('Assoluti', ascending=False).reset_index(drop=True)
            
            # Calcola Supremi
            max_ass = df_finale['Assoluti'].max()
            if max_ass > 0:
                df_finale['Supremi'] = ((df_finale['Assoluti'] / max_ass) * K_FACTOR).round().astype(int)
            else:
                df_finale['Supremi'] = 0
            
            st.session_state.risultati_parziali['Classifica_Finale'] = df_finale
            st.session_state.generale_calcolata = True
        
        # FUORI dallo spinner
        st.success("✅ Classifica Generale calcolata!")
        st.balloons()
    
    # Mostra risultati
    if 'Classifica_Finale' in st.session_state.risultati_parziali:
        st.markdown("### 🏆 Classifica Finale")
        st.dataframe(
            st.session_state.risultati_parziali['Classifica_Finale'],
            use_container_width=True,
            hide_index=True
        )
        
        # Mostra dettagli parziali
        with st.expander("📊 Dettagli Parziali"):
            for key, df in st.session_state.risultati_parziali.items():
                if key != 'Classifica_Finale':
                    st.markdown(f"#### {key}")
                    st.dataframe(df, use_container_width=True, hide_index=True)

# ==================== MAIN ====================

def main():
    """Main app"""
    # Carica dati
    partecipanti, previsioni_class, gironi_data = carica_dati_excel()
    
    if not partecipanti:
        st.error("❌ Impossibile caricare i dati. Verifica che il file Excel sia presente.")
        return
    
    # Inizializza
    inizializza_session_state(partecipanti, gironi_data)
    
    # Sidebar
    with st.sidebar:
        st.title("🏆 Campionato Supremo")
        st.markdown("---")
        
        pagina = st.radio(
            "📍 Navigazione",
            ["📊 Dashboard", "📋 Classifica Squadre"] + 
            [f"⚽ Girone {i}" for i in range(1, 6)] +
            ["📈 Classifica Generale"]
        )
        
        st.markdown("---")
        
        st.markdown("### 📊 Stato Sezioni")
        if st.session_state.classifica_calcolata and not st.session_state.classifica_modificata:
            st.success("✅ Classifica")
        else:
            st.warning("⚠️ Classifica")
        
        for i in range(1, 6):
            if st.session_state[f'girone{i}_calcolato'] and not st.session_state[f'girone{i}_modificato']:
                st.success(f"✅ Girone {i}")
            else:
                st.warning(f"⚠️ Girone {i}")
        
        if st.session_state.generale_calcolata:
            st.success("✅ Generale")
        else:
            st.warning("⚠️ Generale")
    
    # Routing
    if pagina == "📊 Dashboard":
        pagina_dashboard()
    elif pagina == "📋 Classifica Squadre":
        pagina_classifica(partecipanti, previsioni_class)
    elif pagina.startswith("⚽ Girone"):
        num = int(pagina.split()[-1])
        pagina_girone(num, partecipanti, gironi_data)
    elif pagina == "📈 Classifica Generale":
        pagina_generale(partecipanti)

if __name__ == "__main__":
    main()
