# App Campionato Supremo - VERSIONE FINALE v11.0
# Layout Ottimizzato per Smartphone + Frecce Compatte

import streamlit as st
import pandas as pd
import numpy as np
import math
from io import BytesIO

# ==================== CONFIGURAZIONE ====================
K_FACTOR = 25
SOGLIA_GOL_CONTROCORRENTE = 5
SOGLIA_POSIZIONE_CONTROCORRENTE = 4

# ==================== DATI BASE ====================

PARTECIPANTI = ['Teste di calcio', 'Proc', 'Ale', 'Little Eagles', 'Manlio', 
                'Marco Nic', 'ZioMario', 'Francesco', 'Stefano', 'Fernando']

SQUADRE = ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 
           'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli', 
           'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']

CLASSIFICA_DEFAULT = ['Napoli', 'Inter', 'Juventus', 'Milan', 'Roma', 'Fiorentina', 
                      'Atalanta', 'Como', 'Lazio', 'Bologna', 'Torino', 'Udinese', 
                      'Genoa', 'Cagliari', 'Cremonese', 'Parma', 'Sassuolo', 
                      'Lecce', 'Verona', 'Pisa']

# ==================== PREVISIONI CLASSIFICA ====================

PREVISIONI_CLASSIFICA = {
    1: {'Teste di calcio': 'Napoli', 'Proc': 'Inter', 'Ale': 'Napoli', 'Little Eagles': 'Napoli', 'Manlio': 'Napoli', 'Marco Nic': 'Inter', 'ZioMario': 'Juventus', 'Francesco': 'Napoli', 'Stefano': 'Napoli', 'Fernando': 'Napoli'},
    2: {'Teste di calcio': 'Inter', 'Proc': 'Napoli', 'Ale': 'Juventus', 'Little Eagles': 'Inter', 'Manlio': 'Inter', 'Marco Nic': 'Napoli', 'ZioMario': 'Napoli', 'Francesco': 'Juventus', 'Stefano': 'Juventus', 'Fernando': 'Roma'},
    3: {'Teste di calcio': 'Juventus', 'Proc': 'Juventus', 'Ale': 'Inter', 'Little Eagles': 'Juventus', 'Manlio': 'Milan', 'Marco Nic': 'Juventus', 'ZioMario': 'Inter', 'Francesco': 'Inter', 'Stefano': 'Roma', 'Fernando': 'Juventus'},
    4: {'Teste di calcio': 'Roma', 'Proc': 'Milan', 'Ale': 'Milan', 'Little Eagles': 'Milan', 'Manlio': 'Juventus', 'Marco Nic': 'Roma', 'ZioMario': 'Milan', 'Francesco': 'Roma', 'Stefano': 'Milan', 'Fernando': 'Inter'},
    5: {'Teste di calcio': 'Milan', 'Proc': 'Roma', 'Ale': 'Roma', 'Little Eagles': 'Roma', 'Manlio': 'Fiorentina', 'Marco Nic': 'Milan', 'ZioMario': 'Roma', 'Francesco': 'Milan', 'Stefano': 'Inter', 'Fernando': 'Milan'},
    6: {'Teste di calcio': 'Fiorentina', 'Proc': 'Atalanta', 'Ale': 'Lazio', 'Little Eagles': 'Fiorentina', 'Manlio': 'Atalanta', 'Marco Nic': 'Atalanta', 'ZioMario': 'Atalanta', 'Francesco': 'Como', 'Stefano': 'Bologna', 'Fernando': 'Fiorentina'},
    7: {'Teste di calcio': 'Como', 'Proc': 'Fiorentina', 'Ale': 'Fiorentina', 'Little Eagles': 'Bologna', 'Manlio': 'Roma', 'Marco Nic': 'Bologna', 'ZioMario': 'Lazio', 'Francesco': 'Atalanta', 'Stefano': 'Como', 'Fernando': 'Como'},
    8: {'Teste di calcio': 'Lazio', 'Proc': 'Lazio', 'Ale': 'Atalanta', 'Little Eagles': 'Lazio', 'Manlio': 'Lazio', 'Marco Nic': 'Lazio', 'ZioMario': 'Fiorentina', 'Francesco': 'Lazio', 'Stefano': 'Lazio', 'Fernando': 'Atalanta'},
    9: {'Teste di calcio': 'Atalanta', 'Proc': 'Bologna', 'Ale': 'Como', 'Little Eagles': 'Atalanta', 'Manlio': 'Como', 'Marco Nic': 'Fiorentina', 'ZioMario': 'Como', 'Francesco': 'Bologna', 'Stefano': 'Fiorentina', 'Fernando': 'Bologna'},
    10: {'Teste di calcio': 'Bologna', 'Proc': 'Como', 'Ale': 'Bologna', 'Little Eagles': 'Como', 'Manlio': 'Bologna', 'Marco Nic': 'Como', 'ZioMario': 'Bologna', 'Francesco': 'Genoa', 'Stefano': 'Atalanta', 'Fernando': 'Torino'},
    11: {'Teste di calcio': 'Torino', 'Proc': 'Torino', 'Ale': 'Udinese', 'Little Eagles': 'Genoa', 'Manlio': 'Torino', 'Marco Nic': 'Torino', 'ZioMario': 'Torino', 'Francesco': 'Fiorentina', 'Stefano': 'Udinese', 'Fernando': 'Lazio'},
    12: {'Teste di calcio': 'Udinese', 'Proc': 'Genoa', 'Ale': 'Torino', 'Little Eagles': 'Torino', 'Manlio': 'Udinese', 'Marco Nic': 'Udinese', 'ZioMario': 'Udinese', 'Francesco': 'Udinese', 'Stefano': 'Torino', 'Fernando': 'Udinese'},
    13: {'Teste di calcio': 'Genoa', 'Proc': 'Udinese', 'Ale': 'Genoa', 'Little Eagles': 'Udinese', 'Manlio': 'Sassuolo', 'Marco Nic': 'Cremonese', 'ZioMario': 'Genoa', 'Francesco': 'Cagliari', 'Stefano': 'Genoa', 'Fernando': 'Genoa'},
    14: {'Teste di calcio': 'Parma', 'Proc': 'Lecce', 'Ale': 'Cagliari', 'Little Eagles': 'Parma', 'Manlio': 'Parma', 'Marco Nic': 'Genoa', 'ZioMario': 'Lecce', 'Francesco': 'Cremonese', 'Stefano': 'Cagliari', 'Fernando': 'Sassuolo'},
    15: {'Teste di calcio': 'Sassuolo', 'Proc': 'Cagliari', 'Ale': 'Lecce', 'Little Eagles': 'Cremonese', 'Manlio': 'Cremonese', 'Marco Nic': 'Parma', 'ZioMario': 'Parma', 'Francesco': 'Torino', 'Stefano': 'Cremonese', 'Fernando': 'Cagliari'},
    16: {'Teste di calcio': 'Cagliari', 'Proc': 'Cremonese', 'Ale': 'Parma', 'Little Eagles': 'Sassuolo', 'Manlio': 'Cagliari', 'Marco Nic': 'Cagliari', 'ZioMario': 'Verona', 'Francesco': 'Pisa', 'Stefano': 'Parma', 'Fernando': 'Parma'},
    17: {'Teste di calcio': 'Pisa', 'Proc': 'Sassuolo', 'Ale': 'Cremonese', 'Little Eagles': 'Cagliari', 'Manlio': 'Genoa', 'Marco Nic': 'Sassuolo', 'ZioMario': 'Cagliari', 'Francesco': 'Parma', 'Stefano': 'Verona', 'Fernando': 'Lecce'},
    18: {'Teste di calcio': 'Cremonese', 'Proc': 'Parma', 'Ale': 'Verona', 'Little Eagles': 'Verona', 'Manlio': 'Verona', 'Marco Nic': 'Pisa', 'ZioMario': 'Sassuolo', 'Francesco': 'Lecce', 'Stefano': 'Sassuolo', 'Fernando': 'Cremonese'},
    19: {'Teste di calcio': 'Verona', 'Proc': 'Pisa', 'Ale': 'Pisa', 'Little Eagles': 'Lecce', 'Manlio': 'Pisa', 'Marco Nic': 'Lecce', 'ZioMario': 'Cremonese', 'Francesco': 'Sassuolo', 'Stefano': 'Lecce', 'Fernando': 'Verona'},
    20: {'Teste di calcio': 'Lecce', 'Proc': 'Verona', 'Ale': 'Sassuolo', 'Little Eagles': 'Pisa', 'Manlio': 'Lecce', 'Marco Nic': 'Verona', 'ZioMario': 'Pisa', 'Francesco': 'Verona', 'Stefano': 'Pisa', 'Fernando': 'Pisa'},
}

# ==================== GOL MEDI GIOCATORI ====================

GOL_MEDI_GIOCATORI_1 = {'KRSTOVIC Nikola': 9, 'LOOKMAN Ademola Olajade': 8, 'SCAMACCA Gianluca': 11, 'KEAN Moise Bioty': 17, 'MARTINEZ Lautaro Javier': 20, 'THURAM Marcus Lilian': 15, 'DAVID Jonathan Christian': 14, 'OPENDA Ikoma Lois': 7, 'VLAHOVIC Dusan': 11, 'YILDIZ Kenan': 9, 'CASTELLANOS Valentin Mariano': 13, 'GIMENEZ Santiago Tomas': 8, 'LEAO Rafael Alexandre': 13, 'NKUNKU Christopher Alan': 8, 'HOJLUND Rasmus Winther': 13, 'LUCCA Lorenzo': 9, 'LUKAKU Romelu Menama': 9, 'DYBALA Paulo Bruno': 10, 'FERGUSON Evan Joe': 13, "SOULE' Matias": 10}

GOL_MEDI_GIOCATORI_2 = {'DE KETELAERE Charles': 6, 'CASTRO Santiago Tomas': 10, 'ESPOSITO Sebastiano': 9, 'DIAO Assane': 8, 'DOUVIKAS Anastasios': 7, 'MORATA Alvaro Borja': 8, 'VARDY Jamie Richard': 7, 'DZEKO Edin': 6, 'PICCOLI Roberto': 8, 'COLOMBO Lorenzo': 8, 'BONNY Ange-Yoan': 5, 'DIA Boulaye': 7, 'CAMARDA Francesco': 7, 'PELLEGRINO Mateo': 8, 'MEISTER Henrik Wendel': 5, 'DOVBYK Artem': 9, 'BERARDI Domenico': 10, 'PINAMONTI Andrea': 10, 'SIMEONE Giovanni Paolo': 8, 'ZAPATA Duvan Esteban': 9}

GOL_MEDI_GIOCATORI_3 = {'MALDINI Daniel': 5, 'PASALIC Mario': 5, 'SAMARDZIC Lazar Vujadin': 4, 'ODGAARD Jens': 4, 'ORSOLINI Riccardo': 11, 'ROWE Jonathan David': 5, 'PAZ Nicolas': 9, 'GUDMUNDSSON Albert': 7, 'CALHANOGLU Hakan': 8, 'CONCEICAO Francisco Fernandes': 5, 'KOOPMEINERS Teun': 4, 'ZHEGROVA Edon Lulzim': 4, 'ZACCAGNI Mattia': 10, 'LOFTUS-CHEEK Ruben Ira': 5, 'PULISIC Christian Mate': 10, 'RABIOT Adrien': 5, 'DE BRUYNE Kevin': 8, 'MCTOMINAY Scott Francis': 9, 'POLITANO Matteo': 6, 'VLASIC Nikola': 6}

GOL_MEDI_GIOCATORI_4 = {'FERGUSON Lewis': 3, 'MINA Yerry Fernando': 4, 'DA CUNHA Lucas': 4, 'GOSENS Robin': 4, 'MANDRAGORA Rolando': 4, 'DUMFRIES Denzel Justus': 5, 'DIMARCO Federico': 4, 'BISSECK Yann Aurel': 3, 'BREMER Gleison Silva Nascimento': 3, 'THURAM Khephren': 4, 'GUENDOUZI Matteo Elias': 4, 'PAVLOVIC Strahinja': 3, 'DI LORENZO Giovanni': 3, 'BUONGIORNO Alessandro': 3, "ZAMBO ANGUISSA Andre'-Frank": 4, "ANGELINO Jose' Esmoris": 3, 'WESLEY Franca Lima': 4, 'MANCINI Gianluca': 3, "KONE' Kouadio Manu": 3, 'SOLET Oumar': 3}

GOL_MEDI_GIOCATORI_5 = {'BERNARDESCHI Federico': 4, 'IMMOBILE Ciro': 8, 'BELOTTI Andrea': 5, 'ADDAI Jayden Osei': 4, 'KUHN Nicolas-Gerrit': 4, 'RODRIGUEZ Jesus': 4, 'SANABRIA Arnaldo Antonio Ayala': 5, 'VAZQUEZ Franco Damian': 5, 'GRONBAEK Albert': 4, 'FRATTESI Davide': 5, 'ISAKSEN Gustav Tang': 5, 'STULIC Nikola': 5, 'NERES David': 4, 'CUTRONE Patrick': 5, "LAURIENTE' Armand": 5, "ADAMS Che' Zach": 6, 'NGONGE Cyril': 5, 'ATTA Arthur': 5, "ZANIOLO Nicolo'": 5, 'GIOVANE Santana do Nascimento': 6}

# ==================== PREVISIONI GIOCATORI (Tutti i 5 gironi) ====================

PREVISIONI_GIOCATORI_1 = {'KRSTOVIC Nikola': {'Teste di calcio': 10, 'Proc': 6, 'Ale': 12, 'Little Eagles': 10, 'Manlio': 10, 'Marco Nic': 7, 'ZioMario': 8, 'Francesco': 9, 'Stefano': 10, 'Fernando': 10}, 'LOOKMAN Ademola Olajade': {'Teste di calcio': 11, 'Proc': 8, 'Ale': 15, 'Little Eagles': 7, 'Manlio': 12, 'Marco Nic': 3, 'ZioMario': 10, 'Francesco': 5, 'Stefano': 3, 'Fernando': 11}, 'SCAMACCA Gianluca': {'Teste di calcio': 12, 'Proc': 10, 'Ale': 8, 'Little Eagles': 10, 'Manlio': 6, 'Marco Nic': 15, 'ZioMario': 12, 'Francesco': 10, 'Stefano': 12, 'Fernando': 15}, 'KEAN Moise Bioty': {'Teste di calcio': 16, 'Proc': 16, 'Ale': 21, 'Little Eagles': 17, 'Manlio': 24, 'Marco Nic': 16, 'ZioMario': 10, 'Francesco': 18, 'Stefano': 14, 'Fernando': 21}, 'MARTINEZ Lautaro Javier': {'Teste di calcio': 21, 'Proc': 20, 'Ale': 24, 'Little Eagles': 18, 'Manlio': 18, 'Marco Nic': 21, 'ZioMario': 22, 'Francesco': 19, 'Stefano': 15, 'Fernando': 19}, 'THURAM Marcus Lilian': {'Teste di calcio': 14, 'Proc': 12, 'Ale': 17, 'Little Eagles': 12, 'Manlio': 17, 'Marco Nic': 18, 'ZioMario': 16, 'Francesco': 16, 'Stefano': 17, 'Fernando': 18}, 'DAVID Jonathan Christian': {'Teste di calcio': 14, 'Proc': 14, 'Ale': 18, 'Little Eagles': 11, 'Manlio': 12, 'Marco Nic': 15, 'ZioMario': 8, 'Francesco': 16, 'Stefano': 14, 'Fernando': 16}, 'OPENDA Ikoma Lois': {'Teste di calcio': 8, 'Proc': 5, 'Ale': 3, 'Little Eagles': 8, 'Manlio': 9, 'Marco Nic': 7, 'ZioMario': 10, 'Francesco': 9, 'Stefano': 3, 'Fernando': 10}, 'VLAHOVIC Dusan': {'Teste di calcio': 11, 'Proc': 8, 'Ale': 12, 'Little Eagles': 12, 'Manlio': 13, 'Marco Nic': 12, 'ZioMario': 15, 'Francesco': 9, 'Stefano': 8, 'Fernando': 12}, 'YILDIZ Kenan': {'Teste di calcio': 7, 'Proc': 8, 'Ale': 10, 'Little Eagles': 8, 'Manlio': 10, 'Marco Nic': 11, 'ZioMario': 7, 'Francesco': 6, 'Stefano': 10, 'Fernando': 8}, 'CASTELLANOS Valentin Mariano': {'Teste di calcio': 14, 'Proc': 11, 'Ale': 18, 'Little Eagles': 12, 'Manlio': 14, 'Marco Nic': 13, 'ZioMario': 8, 'Francesco': 17, 'Stefano': 10, 'Fernando': 12}, 'GIMENEZ Santiago Tomas': {'Teste di calcio': 8, 'Proc': 9, 'Ale': 7, 'Little Eagles': 8, 'Manlio': 6, 'Marco Nic': 8, 'ZioMario': 5, 'Francesco': 12, 'Stefano': 6, 'Fernando': 11}, 'LEAO Rafael Alexandre': {'Teste di calcio': 13, 'Proc': 11, 'Ale': 10, 'Little Eagles': 12, 'Manlio': 18, 'Marco Nic': 11, 'ZioMario': 14, 'Francesco': 14, 'Stefano': 14, 'Fernando': 10}, 'NKUNKU Christopher Alan': {'Teste di calcio': 9, 'Proc': 6, 'Ale': 8, 'Little Eagles': 6, 'Manlio': 4, 'Marco Nic': 12, 'ZioMario': 9, 'Francesco': 9, 'Stefano': 10, 'Fernando': 8}, 'HOJLUND Rasmus Winther': {'Teste di calcio': 14, 'Proc': 17, 'Ale': 14, 'Little Eagles': 11, 'Manlio': 9, 'Marco Nic': 14, 'ZioMario': 11, 'Francesco': 8, 'Stefano': 17, 'Fernando': 13}, 'LUCCA Lorenzo': {'Teste di calcio': 8, 'Proc': 6, 'Ale': 12, 'Little Eagles': 9, 'Manlio': 12, 'Marco Nic': 8, 'ZioMario': 5, 'Francesco': 12, 'Stefano': 5, 'Fernando': 9}, 'LUKAKU Romelu Menama': {'Teste di calcio': 9, 'Proc': 8, 'Ale': 7, 'Little Eagles': 12, 'Manlio': 9, 'Marco Nic': 10, 'ZioMario': 6, 'Francesco': 10, 'Stefano': 3, 'Fernando': 11}, 'DYBALA Paulo Bruno': {'Teste di calcio': 9, 'Proc': 12, 'Ale': 8, 'Little Eagles': 8, 'Manlio': 16, 'Marco Nic': 7, 'ZioMario': 8, 'Francesco': 15, 'Stefano': 8, 'Fernando': 13}, 'FERGUSON Evan Joe': {'Teste di calcio': 13, 'Proc': 12, 'Ale': 9, 'Little Eagles': 14, 'Manlio': 20, 'Marco Nic': 15, 'ZioMario': 6, 'Francesco': 15, 'Stefano': 14, 'Fernando': 15}, "SOULE' Matias": {'Teste di calcio': 9, 'Proc': 8, 'Ale': 9, 'Little Eagles': 8, 'Manlio': 11, 'Marco Nic': 12, 'ZioMario': 7, 'Francesco': 9, 'Stefano': 12, 'Fernando': 13}}

PREVISIONI_GIOCATORI_2 = {'DE KETELAERE Charles': {'Teste di calcio': 6, 'Proc': 8, 'Ale': 8, 'Little Eagles': 5, 'Manlio': 8, 'Marco Nic': 7, 'ZioMario': 6, 'Francesco': 5, 'Stefano': 4, 'Fernando': 11}, 'CASTRO Santiago Tomas': {'Teste di calcio': 12, 'Proc': 9, 'Ale': 10, 'Little Eagles': 10, 'Manlio': 13, 'Marco Nic': 8, 'ZioMario': 9, 'Francesco': 9, 'Stefano': 7, 'Fernando': 8}, 'ESPOSITO Sebastiano': {'Teste di calcio': 10, 'Proc': 8, 'Ale': 9, 'Little Eagles': 8, 'Manlio': 14, 'Marco Nic': 11, 'ZioMario': 6, 'Francesco': 7, 'Stefano': 6, 'Fernando': 12}, 'DIAO Assane': {'Teste di calcio': 8, 'Proc': 5, 'Ale': 12, 'Little Eagles': 8, 'Manlio': 8, 'Marco Nic': 9, 'ZioMario': 8, 'Francesco': 10, 'Stefano': 5, 'Fernando': 10}, 'DOUVIKAS Anastasios': {'Teste di calcio': 7, 'Proc': 7, 'Ale': 5, 'Little Eagles': 5, 'Manlio': 10, 'Marco Nic': 7, 'ZioMario': 6, 'Francesco': 9, 'Stefano': 6, 'Fernando': 12}, 'MORATA Alvaro Borja': {'Teste di calcio': 10, 'Proc': 6, 'Ale': 4, 'Little Eagles': 9, 'Manlio': 11, 'Marco Nic': 5, 'ZioMario': 7, 'Francesco': 9, 'Stefano': 7, 'Fernando': 11}, 'VARDY Jamie Richard': {'Teste di calcio': 9, 'Proc': 7, 'Ale': 5, 'Little Eagles': 5, 'Manlio': 9, 'Marco Nic': 8, 'ZioMario': 5, 'Francesco': 5, 'Stefano': 6, 'Fernando': 8}, 'DZEKO Edin': {'Teste di calcio': 4, 'Proc': 4, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 9, 'Marco Nic': 6, 'ZioMario': 4, 'Francesco': 8, 'Stefano': 6, 'Fernando': 10}, 'PICCOLI Roberto': {'Teste di calcio': 8, 'Proc': 5, 'Ale': 6, 'Little Eagles': 6, 'Manlio': 7, 'Marco Nic': 8, 'ZioMario': 9, 'Francesco': 9, 'Stefano': 9, 'Fernando': 8}, 'COLOMBO Lorenzo': {'Teste di calcio': 8, 'Proc': 8, 'Ale': 7, 'Little Eagles': 5, 'Manlio': 10, 'Marco Nic': 9, 'ZioMario': 8, 'Francesco': 8, 'Stefano': 5, 'Fernando': 11}, 'BONNY Ange-Yoan': {'Teste di calcio': 5, 'Proc': 5, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 7, 'ZioMario': 5, 'Francesco': 6, 'Stefano': 3, 'Fernando': 6}, 'DIA Boulaye': {'Teste di calcio': 9, 'Proc': 5, 'Ale': 3, 'Little Eagles': 8, 'Manlio': 9, 'Marco Nic': 8, 'ZioMario': 4, 'Francesco': 9, 'Stefano': 4, 'Fernando': 9}, 'CAMARDA Francesco': {'Teste di calcio': 9, 'Proc': 4, 'Ale': 4, 'Little Eagles': 5, 'Manlio': 13, 'Marco Nic': 8, 'ZioMario': 6, 'Francesco': 7, 'Stefano': 4, 'Fernando': 10}, 'PELLEGRINO Mateo': {'Teste di calcio': 9, 'Proc': 6, 'Ale': 4, 'Little Eagles': 7, 'Manlio': 11, 'Marco Nic': 12, 'ZioMario': 6, 'Francesco': 8, 'Stefano': 10, 'Fernando': 11}, 'MEISTER Henrik Wendel': {'Teste di calcio': 8, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 4, 'Marco Nic': 9, 'ZioMario': 4, 'Francesco': 6, 'Stefano': 4, 'Fernando': 6}, 'DOVBYK Artem': {'Teste di calcio': 9, 'Proc': 7, 'Ale': 5, 'Little Eagles': 10, 'Manlio': 9, 'Marco Nic': 11, 'ZioMario': 9, 'Francesco': 10, 'Stefano': 7, 'Fernando': 13}, 'BERARDI Domenico': {'Teste di calcio': 12, 'Proc': 8, 'Ale': 6, 'Little Eagles': 5, 'Manlio': 13, 'Marco Nic': 12, 'ZioMario': 10, 'Francesco': 14, 'Stefano': 7, 'Fernando': 12}, 'PINAMONTI Andrea': {'Teste di calcio': 12, 'Proc': 7, 'Ale': 7, 'Little Eagles': 8, 'Manlio': 14, 'Marco Nic': 14, 'ZioMario': 9, 'Francesco': 8, 'Stefano': 5, 'Fernando': 13}, 'SIMEONE Giovanni Paolo': {'Teste di calcio': 8, 'Proc': 6, 'Ale': 4, 'Little Eagles': 8, 'Manlio': 9, 'Marco Nic': 10, 'ZioMario': 12, 'Francesco': 8, 'Stefano': 5, 'Fernando': 11}, 'ZAPATA Duvan Esteban': {'Teste di calcio': 9, 'Proc': 6, 'Ale': 7, 'Little Eagles': 9, 'Manlio': 14, 'Marco Nic': 8, 'ZioMario': 8, 'Francesco': 14, 'Stefano': 6, 'Fernando': 12}}

PREVISIONI_GIOCATORI_3 = {'MALDINI Daniel': {'Teste di calcio': 6, 'Proc': 5, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 8, 'Marco Nic': 5, 'ZioMario': 6, 'Francesco': 6, 'Stefano': 3, 'Fernando': 6}, 'PASALIC Mario': {'Teste di calcio': 6, 'Proc': 3, 'Ale': 4, 'Little Eagles': 5, 'Manlio': 9, 'Marco Nic': 4, 'ZioMario': 5, 'Francesco': 4, 'Stefano': 5, 'Fernando': 9}, 'SAMARDZIC Lazar Vujadin': {'Teste di calcio': 3, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 4, 'Marco Nic': 4, 'ZioMario': 4, 'Francesco': 4, 'Stefano': 3, 'Fernando': 5}, 'ODGAARD Jens': {'Teste di calcio': 6, 'Proc': 5, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 5, 'ZioMario': 4, 'Francesco': 6, 'Stefano': 4, 'Fernando': 3}, 'ORSOLINI Riccardo': {'Teste di calcio': 11, 'Proc': 8, 'Ale': 9, 'Little Eagles': 9, 'Manlio': 16, 'Marco Nic': 13, 'ZioMario': 6, 'Francesco': 15, 'Stefano': 8, 'Fernando': 11}, 'ROWE Jonathan David': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 9, 'Marco Nic': 7, 'ZioMario': 4, 'Francesco': 4, 'Stefano': 3, 'Fernando': 4}, 'PAZ Nicolas': {'Teste di calcio': 8, 'Proc': 8, 'Ale': 7, 'Little Eagles': 8, 'Manlio': 11, 'Marco Nic': 8, 'ZioMario': 8, 'Francesco': 11, 'Stefano': 6, 'Fernando': 11}, 'GUDMUNDSSON Albert': {'Teste di calcio': 7, 'Proc': 8, 'Ale': 3, 'Little Eagles': 7, 'Manlio': 9, 'Marco Nic': 12, 'ZioMario': 5, 'Francesco': 6, 'Stefano': 3, 'Fernando': 10}, 'CALHANOGLU Hakan': {'Teste di calcio': 5, 'Proc': 6, 'Ale': 5, 'Little Eagles': 6, 'Manlio': 16, 'Marco Nic': 9, 'ZioMario': 7, 'Francesco': 10, 'Stefano': 6, 'Fernando': 8}, 'CONCEICAO Francisco Fernandes': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 9, 'Marco Nic': 6, 'ZioMario': 6, 'Francesco': 5, 'Stefano': 5, 'Fernando': 4}, 'KOOPMEINERS Teun': {'Teste di calcio': 3, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 6, 'Marco Nic': 4, 'ZioMario': 5, 'Francesco': 5, 'Stefano': 3, 'Fernando': 6}, 'ZHEGROVA Edon Lulzim': {'Teste di calcio': 4, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 4, 'Marco Nic': 5, 'ZioMario': 6, 'Francesco': 6, 'Stefano': 4, 'Fernando': 3}, 'ZACCAGNI Mattia': {'Teste di calcio': 9, 'Proc': 9, 'Ale': 12, 'Little Eagles': 12, 'Manlio': 15, 'Marco Nic': 9, 'ZioMario': 8, 'Francesco': 10, 'Stefano': 9, 'Fernando': 8}, 'LOFTUS-CHEEK Ruben Ira': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 6, 'Manlio': 9, 'Marco Nic': 3, 'ZioMario': 4, 'Francesco': 7, 'Stefano': 4, 'Fernando': 5}, 'PULISIC Christian Mate': {'Teste di calcio': 10, 'Proc': 8, 'Ale': 8, 'Little Eagles': 8, 'Manlio': 16, 'Marco Nic': 11, 'ZioMario': 8, 'Francesco': 13, 'Stefano': 7, 'Fernando': 9}, 'RABIOT Adrien': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 3, 'ZioMario': 5, 'Francesco': 6, 'Stefano': 6, 'Fernando': 6}, 'DE BRUYNE Kevin': {'Teste di calcio': 7, 'Proc': 6, 'Ale': 4, 'Little Eagles': 6, 'Manlio': 8, 'Marco Nic': 6, 'ZioMario': 7, 'Francesco': 11, 'Stefano': 9, 'Fernando': 11}, 'MCTOMINAY Scott Francis': {'Teste di calcio': 10, 'Proc': 5, 'Ale': 7, 'Little Eagles': 7, 'Manlio': 10, 'Marco Nic': 10, 'ZioMario': 8, 'Francesco': 10, 'Stefano': 10, 'Fernando': 13}, 'POLITANO Matteo': {'Teste di calcio': 3, 'Proc': 6, 'Ale': 3, 'Little Eagles': 6, 'Manlio': 4, 'Marco Nic': 5, 'ZioMario': 8, 'Francesco': 7, 'Stefano': 6, 'Fernando': 9}, 'VLASIC Nikola': {'Teste di calcio': 5, 'Proc': 6, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 11, 'Marco Nic': 3, 'ZioMario': 7, 'Francesco': 6, 'Stefano': 5, 'Fernando': 6}}

PREVISIONI_GIOCATORI_4 = {'FERGUSON Lewis': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 8, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 5}, 'MINA Yerry Fernando': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 12, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 4}, 'DA CUNHA Lucas': {'Teste di calcio': 5, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 10, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 4}, 'GOSENS Robin': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 7, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 4}, 'MANDRAGORA Rolando': {'Teste di calcio': 4, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 7, 'Marco Nic': 5, 'ZioMario': 3, 'Francesco': 6, 'Stefano': 5, 'Fernando': 4}, 'DUMFRIES Denzel Justus': {'Teste di calcio': 6, 'Proc': 5, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 8, 'Marco Nic': 7, 'ZioMario': 4, 'Francesco': 4, 'Stefano': 5, 'Fernando': 5}, 'DIMARCO Federico': {'Teste di calcio': 3, 'Proc': 5, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 7, 'Marco Nic': 5, 'ZioMario': 3, 'Francesco': 5, 'Stefano': 3, 'Fernando': 6}, 'BISSECK Yann Aurel': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 3}, 'BREMER Gleison Silva Nascimento': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 5}, 'THURAM Khephren': {'Teste di calcio': 4, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 9, 'Marco Nic': 4, 'ZioMario': 4, 'Francesco': 5, 'Stefano': 3, 'Fernando': 5}, 'GUENDOUZI Matteo Elias': {'Teste di calcio': 3, 'Proc': 4, 'Ale': 4, 'Little Eagles': 3, 'Manlio': 8, 'Marco Nic': 3, 'ZioMario': 4, 'Francesco': 5, 'Stefano': 3, 'Fernando': 4}, 'PAVLOVIC Strahinja': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 3}, 'DI LORENZO Giovanni': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 4}, 'BUONGIORNO Alessandro': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 3}, "ZAMBO ANGUISSA Andre'-Frank": {'Teste di calcio': 4, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 6, 'Marco Nic': 4, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 4, 'Fernando': 6}, "ANGELINO Jose' Esmoris": {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 4, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 5, 'Stefano': 3, 'Fernando': 5}, 'WESLEY Franca Lima': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 6}, 'MANCINI Gianluca': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 4, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 5}, "KONE' Kouadio Manu": {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 4, 'Fernando': 5}, 'SOLET Oumar': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 3, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 4}}

PREVISIONI_GIOCATORI_5 = {'BERNARDESCHI Federico': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 7, 'Marco Nic': 4, 'ZioMario': 7, 'Francesco': 5, 'Stefano': 3, 'Fernando': 6}, 'IMMOBILE Ciro': {'Teste di calcio': 7, 'Proc': 8, 'Ale': 6, 'Little Eagles': 6, 'Manlio': 12, 'Marco Nic': 8, 'ZioMario': 6, 'Francesco': 5, 'Stefano': 7, 'Fernando': 15}, 'BELOTTI Andrea': {'Teste di calcio': 6, 'Proc': 7, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 5, 'Marco Nic': 5, 'ZioMario': 5, 'Francesco': 3, 'Stefano': 3, 'Fernando': 6}, 'ADDAI Jayden Osei': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 8, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 5}, 'KUHN Nicolas-Gerrit': {'Teste di calcio': 4, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 7, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 6}, 'RODRIGUEZ Jesus': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 10, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 3, 'Stefano': 3, 'Fernando': 4}, 'SANABRIA Arnaldo Antonio Ayala': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 10, 'Marco Nic': 3, 'ZioMario': 5, 'Francesco': 6, 'Stefano': 4, 'Fernando': 9}, 'VAZQUEZ Franco Damian': {'Teste di calcio': 6, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 12, 'Marco Nic': 6, 'ZioMario': 4, 'Francesco': 5, 'Stefano': 4, 'Fernando': 6}, 'GRONBAEK Albert': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 9, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 6}, 'FRATTESI Davide': {'Teste di calcio': 3, 'Proc': 3, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 8, 'Marco Nic': 5, 'ZioMario': 4, 'Francesco': 5, 'Stefano': 5, 'Fernando': 8}, 'ISAKSEN Gustav Tang': {'Teste di calcio': 3, 'Proc': 5, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 8, 'Marco Nic': 4, 'ZioMario': 7, 'Francesco': 3, 'Stefano': 4, 'Fernando': 6}, 'STULIC Nikola': {'Teste di calcio': 9, 'Proc': 7, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 6, 'Marco Nic': 3, 'ZioMario': 6, 'Francesco': 8, 'Stefano': 3, 'Fernando': 5}, 'NERES David': {'Teste di calcio': 3, 'Proc': 4, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 7, 'Marco Nic': 4, 'ZioMario': 3, 'Francesco': 6, 'Stefano': 3, 'Fernando': 5}, 'CUTRONE Patrick': {'Teste di calcio': 5, 'Proc': 4, 'Ale': 5, 'Little Eagles': 4, 'Manlio': 8, 'Marco Nic': 8, 'ZioMario': 4, 'Francesco': 5, 'Stefano': 3, 'Fernando': 7}, "LAURIENTE' Armand": {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 5, 'Manlio': 8, 'Marco Nic': 3, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 3, 'Fernando': 9}, "ADAMS Che' Zach": {'Teste di calcio': 7, 'Proc': 4, 'Ale': 3, 'Little Eagles': 4, 'Manlio': 8, 'Marco Nic': 5, 'ZioMario': 5, 'Francesco': 7, 'Stefano': 5, 'Fernando': 10}, 'NGONGE Cyril': {'Teste di calcio': 4, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 9, 'Marco Nic': 6, 'ZioMario': 6, 'Francesco': 7, 'Stefano': 4, 'Fernando': 3}, 'ATTA Arthur': {'Teste di calcio': 5, 'Proc': 3, 'Ale': 5, 'Little Eagles': 3, 'Manlio': 9, 'Marco Nic': 4, 'ZioMario': 3, 'Francesco': 4, 'Stefano': 5, 'Fernando': 3}, "ZANIOLO Nicolo'": {'Teste di calcio': 5, 'Proc': 4, 'Ale': 3, 'Little Eagles': 3, 'Manlio': 7, 'Marco Nic': 5, 'ZioMario': 4, 'Francesco': 3, 'Stefano': 3, 'Fernando': 8}, 'GIOVANE Santana do Nascimento': {'Teste di calcio': 7, 'Proc': 3, 'Ale': 6, 'Little Eagles': 3, 'Manlio': 14, 'Marco Nic': 7, 'ZioMario': 3, 'Francesco': 5, 'Stefano': 6, 'Fernando': 4}}

# ==================== FUNZIONI ====================

def calcola_punteggio_giocatore(pronosticati, reali):
    """Calcola punteggio per singolo giocatore"""
    if pd.isna(reali) or reali < 3:
        return 0
    errore = abs(pronosticati - reali)
    malus = errore ** 2
    return max(0, reali - malus)

def calcola_punteggio_base_squadra(prevista, reale):
    """Calcola punteggio base per posizione squadra"""
    errore = abs(prevista - reale)
    return max(0, 10 - (errore ** 2))

def valida_numero_gol(input_str):
    """Valida input gol - restituisce (is_valid, valore, messaggio_errore)"""
    if not input_str or input_str.strip() == "":
        return True, 0, ""
    
    try:
        valore = int(input_str)
        if valore < 0:
            return False, 0, "❌ Il numero deve essere positivo"
        if valore > 50:
            return False, 0, "❌ Massimo 50 gol"
        return True, valore, ""
    except ValueError:
        return False, 0, "❌ Inserisci SOLO un numero intero"

# ==================== CONFIGURAZIONE APP ====================

st.set_page_config(page_title="Campionato Supremo", page_icon="⚽", layout="wide")

# CSS per layout compatto ottimizzato per mobile
st.markdown("""
<style>
    /* Compatta layout generale */
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    
    /* Riduce spazio tra le righe */
    div[data-testid="column"] {padding: 2px 4px;}
    
    /* Pulsanti frecce compatti */
    div[data-testid="column"] button {
        padding: 4px 8px !important;
        font-size: 16px !important;
        min-height: 32px !important;
        height: 32px !important;
    }
    
    /* Forza layout orizzontale su mobile */
    @media (max-width: 640px) {
        div[data-testid="column"] {
            flex: 1 1 auto !important;
            min-width: 0 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ Campionato Supremo")

st.sidebar.title("📊 Menu")
pagina = st.sidebar.radio("", ["🏆 Dashboard", "📋 Classifica", "⚽ Girone 1", "⚽ Girone 2", "⚽ Girone 3", "⚽ Girone 4", "⚽ Girone 5", "📈 Risultati"])

# ==================== INIZIALIZZAZIONE ====================

if 'classifica_list' not in st.session_state:
    st.session_state.classifica_list = CLASSIFICA_DEFAULT.copy()

if 'gol_giocatori' not in st.session_state:
    st.session_state.gol_giocatori = {
        'Giocatori_1': GOL_MEDI_GIOCATORI_1.copy(),
        'Giocatori_2': GOL_MEDI_GIOCATORI_2.copy(),
        'Giocatori_3': GOL_MEDI_GIOCATORI_3.copy(),
        'Giocatori_4': GOL_MEDI_GIOCATORI_4.copy(),
        'Giocatori_5': GOL_MEDI_GIOCATORI_5.copy(),
    }

if 'risultati_parziali' not in st.session_state:
    st.session_state.risultati_parziali = {}

if 'errori_validazione' not in st.session_state:
    st.session_state.errori_validazione = {}

# ==================== DASHBOARD ====================

if pagina == "🏆 Dashboard":
    st.header("Dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Partecipanti", len(PARTECIPANTI))
    c2.metric("🏟️ Squadre", 20)
    c3.metric("⚽ Giocatori", 100)
    
    st.subheader("📋 Classifica Attuale")
    df_class = pd.DataFrame(enumerate(st.session_state.classifica_list, 1), columns=['Pos', 'Squadra'])
    st.dataframe(df_class, hide_index=True, use_container_width=True)
    
    if st.session_state.risultati_parziali:
        st.subheader("📊 Simulazioni Parziali")
        for sez, ris in st.session_state.risultati_parziali.items():
            with st.expander(f"🏆 {sez}"):
                st.dataframe(ris, use_container_width=True, hide_index=True)

# ==================== CLASSIFICA CON FRECCE COMPATTE ====================

elif pagina == "📋 Classifica":
    st.header("🏟️ Classifica Squadre")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔄 Reset Classifica"):
            st.session_state.classifica_list = CLASSIFICA_DEFAULT.copy()
            if 'Classifica' in st.session_state.risultati_parziali:
                del st.session_state.risultati_parziali['Classifica']
            st.rerun()
    
    st.info("💡 **Riordina**: ⬆️ su | ⬇️ giù")
    
    # Layout compatto ottimizzato per mobile
    for i in range(20):
        cols = st.columns([5, 1, 1])
        
        with cols[0]:
            st.write(f"**{i+1}. {st.session_state.classifica_list[i]}**")
        
        with cols[1]:
            if st.button("⬆️", key=f"up_{i}", disabled=(i == 0), help="Sposta su"):
                st.session_state.classifica_list[i], st.session_state.classifica_list[i-1] = \
                    st.session_state.classifica_list[i-1], st.session_state.classifica_list[i]
                st.rerun()
        
        with cols[2]:
            if st.button("⬇️", key=f"down_{i}", disabled=(i == 19), help="Sposta giù"):
                st.session_state.classifica_list[i], st.session_state.classifica_list[i+1] = \
                    st.session_state.classifica_list[i+1], st.session_state.classifica_list[i]
                st.rerun()
    
    st.success("✅ Tutte le 20 squadre inserite")
    
    with c2:
        simula_class = st.button("🧮 Simula Classifica", type="primary")
    
    if simula_class:
        with st.spinner("Calcolo classifica..."):
            mappa_reali = {sq: i+1 for i, sq in enumerate(st.session_state.classifica_list)}
            mappe_prev = {}
            
            for part in PARTECIPANTI:
                mappa = {}
                for sq in st.session_state.classifica_list:
                    for pos, d in PREVISIONI_CLASSIFICA.items():
                        if d.get(part) == sq:
                            mappa[sq] = pos
                            break
                mappe_prev[part] = mappa
            
            punti_class = {}
            for part in PARTECIPANTI:
                tot = bonus = cc = 0
                for sq in st.session_state.classifica_list:
                    reale = mappa_reali[sq]
                    prev = mappe_prev[part].get(sq, 99)
                    err = abs(prev - reale)
                    tot += calcola_punteggio_base_squadra(prev, reale)
                    
                    if err == 0:
                        if reale == 1:
                            bonus += 10
                        elif 2 <= reale <= 4:
                            bonus += 3
                        elif 5 <= reale <= 6:
                            bonus += 2
                        elif 18 <= reale <= 20:
                            bonus += 4
                    
                    altri = [mappe_prev[p].get(sq, 99) for p in PARTECIPANTI if p != part]
                    pmc = np.mean(altri)
                    
                    if abs(prev - pmc) >= SOGLIA_POSIZIONE_CONTROCORRENTE:
                        if err == 0:
                            cc += 5
                        elif err == 1:
                            cc += 3
                        elif err > 2 and err > abs(round(pmc) - reale):
                            cc -= 5
                
                punti_class[part] = tot + bonus + cc
            
            max_p = max(punti_class.values())
            orac = [p for p, pt in punti_class.items() if pt == max_p]
            if orac:
                bo = math.ceil(10 / len(orac))
                for o in orac:
                    punti_class[o] += bo
            
            df_ris = pd.DataFrame(list(punti_class.items()), columns=['Partecipante', 'Assoluti'])
            df_ris = df_ris.sort_values('Assoluti', ascending=False)
            max_ass = df_ris['Assoluti'].max()
            df_ris['Supremi'] = ((df_ris['Assoluti'] / max_ass) * K_FACTOR).round().astype(int) if max_ass > 0 else 0
            
            st.session_state.risultati_parziali['Classifica'] = df_ris
            st.success("✅ Simulazione completata!")
            st.dataframe(df_ris, use_container_width=True, hide_index=True)

# ==================== GIRONI CON VALIDAZIONE ====================

elif pagina.startswith("⚽ Girone"):
    num = pagina.split()[-1]
    nome = f"Giocatori_{num}"
    
    if num == "1":
        gol_medi = GOL_MEDI_GIOCATORI_1
        previsioni = PREVISIONI_GIOCATORI_1
    elif num == "2":
        gol_medi = GOL_MEDI_GIOCATORI_2
        previsioni = PREVISIONI_GIOCATORI_2
    elif num == "3":
        gol_medi = GOL_MEDI_GIOCATORI_3
        previsioni = PREVISIONI_GIOCATORI_3
    elif num == "4":
        gol_medi = GOL_MEDI_GIOCATORI_4
        previsioni = PREVISIONI_GIOCATORI_4
    else:
        gol_medi = GOL_MEDI_GIOCATORI_5
        previsioni = PREVISIONI_GIOCATORI_5
    
    st.header(f"⚽ {nome}")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(f"🔄 Reset {nome}", key=f"rst_{nome}"):
            st.session_state.gol_giocatori[nome] = gol_medi.copy()
            if nome in st.session_state.risultati_parziali:
                del st.session_state.risultati_parziali[nome]
            st.session_state.errori_validazione = {}
            st.rerun()
    
    st.info("💡 **Validazione attiva**: Inserisci SOLO numeri interi da 0 a 50")
    
    st.markdown("<style>.error-gol {color: red; font-size: 11px; margin-top: -8px; font-weight: bold;}</style>", unsafe_allow_html=True)
    
    errori_presenti = False
    
    for gioc in gol_medi.keys():
        col_g, col_gol = st.columns([2, 1])
        
        with col_g:
            st.write(f"**{gioc}**")
            if previsioni and gioc in previsioni:
                prev_list = [f"{p}: {previsioni[gioc][p]}" for p in PARTECIPANTI if p in previsioni[gioc]]
                st.caption(" | ".join(prev_list))
        
        with col_gol:
            val_att = st.session_state.gol_giocatori[nome][gioc]
            inp = st.text_input("Gol", value=str(int(val_att)), key=f"{nome}_{gioc}", label_visibility="collapsed")
            
            is_valid, valore, msg_err = valida_numero_gol(inp)
            
            if is_valid:
                st.session_state.gol_giocatori[nome][gioc] = valore
                if f"{nome}_{gioc}" in st.session_state.errori_validazione:
                    del st.session_state.errori_validazione[f"{nome}_{gioc}"]
            else:
                st.session_state.errori_validazione[f"{nome}_{gioc}"] = msg_err
                errori_presenti = True
                st.markdown(f"<p class='error-gol'>{msg_err}</p>", unsafe_allow_html=True)
    
    with c2:
        simula_gir = st.button(f"🧮 Simula {nome}", type="primary", key=f"sim_{nome}", disabled=errori_presenti)
    
    if errori_presenti:
        st.error("⚠️ Correggi gli errori prima di simulare")
    
    if simula_gir and not errori_presenti:
        with st.spinner(f"Calcolo {nome}..."):
            pg = {}
            for part in PARTECIPANTI:
                tot = 0
                for gioc in gol_medi.keys():
                    if gioc in previsioni and part in previsioni[gioc]:
                        pron = previsioni[gioc][part]
                        reale = st.session_state.gol_giocatori[nome][gioc]
                        tot += calcola_punteggio_giocatore(pron, reale)
                pg[part] = tot
            
            df_ris = pd.DataFrame(list(pg.items()), columns=['Partecipante', 'Assoluti'])
            df_ris = df_ris.sort_values('Assoluti', ascending=False)
            max_ass = df_ris['Assoluti'].max()
            df_ris['Supremi'] = ((df_ris['Assoluti'] / max_ass) * K_FACTOR).round().astype(int) if max_ass > 0 else 0
            
            st.session_state.risultati_parziali[nome] = df_ris
            st.success("✅ Simulazione completata!")
            st.dataframe(df_ris, use_container_width=True, hide_index=True)

# ==================== RISULTATI FINALI ====================

elif pagina == "📈 Risultati":
    st.header("🏆 Risultati Finali")
    st.info("📊 Calcola i risultati finali con tutti i dati inseriti")
    
    if st.button("🧮 Calcola Totale", type="primary", use_container_width=True):
        with st.spinner("Calcolo totale..."):
            punt_gir = {p: {} for p in PARTECIPANTI}
            
            for n in range(1, 6):
                nome = f"Giocatori_{n}"
                if n == 1:
                    prev = PREVISIONI_GIOCATORI_1
                elif n == 2:
                    prev = PREVISIONI_GIOCATORI_2
                elif n == 3:
                    prev = PREVISIONI_GIOCATORI_3
                elif n == 4:
                    prev = PREVISIONI_GIOCATORI_4
                else:
                    prev = PREVISIONI_GIOCATORI_5
                
                for p in PARTECIPANTI:
                    tot = 0
                    for gioc, pd_dict in prev.items():
                        if p in pd_dict:
                            pron = pd_dict[p]
                            reale = st.session_state.gol_giocatori[nome][gioc]
                            tot += calcola_punteggio_giocatore(pron, reale)
                    punt_gir[p][f"Girone {n}"] = tot
            
            mappa_reali = {sq: i+1 for i, sq in enumerate(st.session_state.classifica_list)}
            mappe_prev = {}
            for p in PARTECIPANTI:
                m = {}
                for sq in st.session_state.classifica_list:
                    for pos, d in PREVISIONI_CLASSIFICA.items():
                        if d.get(p) == sq:
                            m[sq] = pos
                            break
                mappe_prev[p] = m
            
            punti_class = {}
            for p in PARTECIPANTI:
                tot = bonus = cc = 0
                for sq in st.session_state.classifica_list:
                    reale = mappa_reali[sq]
                    prev = mappe_prev[p].get(sq, 99)
                    err = abs(prev - reale)
                    tot += calcola_punteggio_base_squadra(prev, reale)
                    if err == 0:
                        if reale == 1:
                            bonus += 10
                        elif 2 <= reale <= 4:
                            bonus += 3
                        elif 5 <= reale <= 6:
                            bonus += 2
                        elif 18 <= reale <= 20:
                            bonus += 4
                    altri = [mappe_prev[x].get(sq, 99) for x in PARTECIPANTI if x != p]
                    pmc = np.mean(altri)
                    if abs(prev - pmc) >= SOGLIA_POSIZIONE_CONTROCORRENTE:
                        if err == 0:
                            cc += 5
                        elif err == 1:
                            cc += 3
                        elif err > 2 and err > abs(round(pmc) - reale):
                            cc -= 5
                punti_class[p] = tot + bonus + cc
            
            max_p = max(punti_class.values())
            orac = [p for p, pt in punti_class.items() if pt == max_p]
            if orac:
                bo = math.ceil(10 / len(orac))
                for o in orac:
                    punti_class[o] += bo
            
            df_int = pd.DataFrame(punt_gir).T
            df_int['Classifica Squadre'] = pd.Series(punti_class)
            
            df_sup = pd.DataFrame(index=PARTECIPANTI)
            for col in df_int.columns:
                mv = df_int[col].max()
                df_sup[col] = ((df_int[col] / mv) * K_FACTOR).round().astype(int) if mv > 0 else 0
            
            df_tab_sup = df_sup.copy()
            df_tab_sup['Totali Supremi'] = df_sup.sum(axis=1)
            df_tab_sup = df_tab_sup.sort_values('Totali Supremi', ascending=False)
            co = ['Totali Supremi', 'Classifica Squadre'] + [f'Girone {i}' for i in range(1, 6)]
            df_tab_sup = df_tab_sup[[c for c in co if c in df_tab_sup.columns]]
            
            df_tab_ass = df_int.copy()
            df_tab_ass['Totali Assoluti'] = df_int.sum(axis=1)
            df_tab_ass = df_tab_ass.reindex(df_tab_sup.index)
            coa = ['Totali Assoluti', 'Classifica Squadre'] + [f'Girone {i}' for i in range(1, 6)]
            df_tab_ass = df_tab_ass[[c for c in coa if c in df_tab_ass.columns]]
        
        st.success("✅ Calcolo completato!")
        
        st.subheader("🏆 Classifica Suprema")
        st.dataframe(df_tab_sup, use_container_width=True)
        
        st.subheader("📊 Classifica Assoluta")
        st.dataframe(df_tab_ass, use_container_width=True)
        
        st.subheader("💾 Download")
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            df_tab_sup.to_excel(w, sheet_name='Suprema')
            df_tab_ass.to_excel(w, sheet_name='Assoluta')
        out.seek(0)
        
        st.download_button("📥 Scarica Excel", data=out.getvalue(), file_name="Risultati_Campionato_Supremo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.sidebar.markdown("---")
st.sidebar.markdown("⚽ **Campionato Supremo v11.0 FINALE**")
st.sidebar.caption("Layout Ottimizzato Smartphone")
