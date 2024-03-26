# import
import pandas as pd
from tqdm import tqdm

def conversion(nb_val, indice, df_monnaie):
    return(nb_val / df_monnaie["rate"].iloc[indice - 2])

def conversion_conso(i, liste_soluce):
    if(liste_soluce["code_unite_energie"].iloc[i] == 2):
        return([2.7778 * liste_soluce["energie_gain"].iloc[i] * 1000000 / 10000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 3):
        return([liste_soluce["energie_gain"].iloc[i] * 1000000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 12):
        return([liste_soluce["energie_gain"].iloc[i] * 1000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 5):
        return([liste_soluce["energie_gain"].iloc[i], 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 37):
        return([liste_soluce["energie_gain"].iloc[i] / 1000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 11):
        return([liste_soluce["energie_gain"].iloc[i] / 1.0551 / 1000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 14):
        return([42 * liste_soluce["energie_gain"].iloc[i] / (2.7778 * 10000) * 1000000, 0])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 7):
        return([liste_soluce["energie_gain"].iloc[i] / 1000, 1])
    elif(liste_soluce["code_unite_energie"].iloc[i] == 9):
        return([liste_soluce["energie_gain"].iloc[i], 1])
    else:
        return([0, -1])

def conversion_taux(taux):
    taux = round(taux / 100, 2)
    if(taux < 0.2):
        taux = 1
    elif(taux < 0.4):
        taux = 2
    elif(taux < 0.6):
        taux = 3
    elif(taux < 0.8):
        taux = 4
    else:
        taux = 5
    return(taux)

def calcul_cout_pondere(num_solution):
    df_soluce = pd.read_csv('../data/solution_rex.csv')
    df_monnaie = pd.read_csv('../data/monnaie.csv')
    liste_soluce = df_soluce[(df_soluce['numsolution'] == int(num_solution))]

    consommation = [0, 0]
    taux_conso = [0, 0]
    nb_conso = [0, 0]
    nb_poids_conso = [0, 0]

    gain = 0
    taux_gain = 0
    nb_gain = 0
    nb_poids_gain = 0

    co2 = 0
    taux_co2 = 0
    nb_co2 = 0
    nb_poids_co2 = 0
    
    cout = 0
    taux_cout = 0
    nb_cout = 0
    nb_poids_cout = 0

    for i in range(len(liste_soluce)):

        presence_conso_ene = 0
        presence_conso_eau = 0
        presence_gain = 0
        presence_co2 = 0
        presence_cout = 0
        tot = 0

        if(not pd.isna(liste_soluce["energie_gain"].iloc[i])):
            tempo = conversion_conso(i, liste_soluce)
            if(tempo[1] != -1):
                if(tempo[1] == 1):
                    presence_conso_eau = tempo[0]
                else:
                    presence_conso_ene = tempo[0]
                nb_conso[tempo[1]] += 1
                tot += 1

        if(not pd.isna(liste_soluce["gain"].iloc[i])):
            presence_gain = conversion(liste_soluce["gain"].iloc[i], liste_soluce["code_monnaie_gain"].iloc[i], df_monnaie)
            nb_gain += 1
            tot += 1
            
        if(not pd.isna(liste_soluce["ges_gain"].iloc[i])):
            presence_co2 = liste_soluce["ges_gain"].iloc[i]
            nb_co2 += 1
            tot += 1

        if(not pd.isna(liste_soluce["reel_cout"].iloc[i]) and liste_soluce["reel_cout"].iloc[i] != 0):
            presence_cout = conversion(liste_soluce["reel_cout"].iloc[i], liste_soluce["code_monnaie_cout"].iloc[i], df_monnaie)
            nb_cout += 1
            tot += 1
        elif((not pd.isna(liste_soluce["mini_cout"].iloc[i]) and liste_soluce["mini_cout"].iloc[i] != 0) and (not pd.isna(liste_soluce["maxi_cout"].iloc[i]) and liste_soluce["maxi_cout"].iloc[i] != 0)):
            cout_temp = (liste_soluce["mini_cout"].iloc[i] + liste_soluce["maxi_cout"].iloc[i]) / 2
            presence_cout = conversion(cout_temp, liste_soluce["code_monnaie_cout"].iloc[i], df_monnaie)
            nb_cout += 1
            tot += 1
        
        if tot == 4:
            ponderation = 1
        elif tot == 3:
            ponderation = 0.66
        elif tot == 2:
            ponderation = 0.4
        elif tot == 1:
            ponderation = 0.15

        if(tot != 0):
            if(presence_conso_ene != 0 and not pd.isna(presence_conso_ene)):
                consommation[0] += ponderation * presence_conso_ene
                taux_conso[0] += tot / 4 * 100
                nb_poids_conso[0] += ponderation

            if(presence_conso_eau != 0 and not pd.isna(presence_conso_eau)):
                consommation[1] += ponderation * presence_conso_eau
                taux_conso[1] += tot / 4 * 100
                nb_poids_conso[1] += ponderation

            if(presence_gain != 0 and not pd.isna(presence_gain)):
                gain += ponderation * presence_gain
                taux_gain += tot / 4 * 100
                nb_poids_gain += ponderation

            if(presence_co2 != 0 and not pd.isna(presence_co2)):
                co2 += ponderation * presence_co2
                taux_co2 += tot / 4 * 100
                nb_poids_co2 += ponderation

            if(presence_cout != 0 and not pd.isna(presence_cout)):
                cout += ponderation * presence_cout
                taux_cout += tot / 4 * 100
                nb_poids_cout += ponderation
    
    if(nb_poids_conso[0] != 0 and nb_poids_conso[1] != 0):
        gain_ene = consommation[0] / nb_poids_conso[0]
        taux_ene = taux_conso[0]/nb_conso[0]
        gain_eau = consommation[1] / nb_poids_conso[1]
        taux_eau = taux_conso[1]/nb_conso[1]
    elif(nb_poids_conso[0] != 0):
        gain_ene = consommation[0] / nb_poids_conso[0]
        taux_ene = taux_conso[0]/nb_conso[0]
        gain_eau = 0
        taux_eau = 0
    elif(nb_poids_conso[1] != 0):
        gain_ene = 0
        taux_ene = 0
        gain_eau = consommation[1] / nb_poids_conso[1]
        taux_eau = taux_conso[1]/nb_conso[1]
    else:
        gain_ene = 0
        taux_ene = 0
        gain_eau = 0
        taux_eau = 0
    
    if(nb_poids_gain != 0):
        gain = gain / nb_poids_gain
        taux_gain = taux_gain/nb_gain
    else:
        gain = 0
        taux_gain = 0

    if(nb_poids_co2 != 0):
        co2 = co2 / nb_poids_co2
        taux_co2 = taux_co2/nb_co2
    else:
        co2 = 0
        taux_co2 = 0
    
    if(nb_poids_cout != 0):
        cout = cout / nb_poids_cout
        taux_cout = taux_cout/nb_cout
    else:
        cout = 0
        taux_cout = 0
    
    taux_ene = conversion_taux(taux_ene)
    taux_eau = conversion_taux(taux_eau)
    taux_gain = conversion_taux(taux_gain)
    taux_co2 = conversion_taux(taux_co2)
    taux_cout = conversion_taux(taux_cout)
    
    return([gain_ene, taux_ene, gain_eau, taux_eau, gain, taux_gain, co2, taux_co2, cout, taux_cout, len(liste_soluce)])

def writing_csv():
    df_solution = pd.read_csv('../data/solution.csv')
    liste_solution = df_solution[(df_solution['codelangue'] == int(2))]
    num_solution = []
    nb_solution = []
    gain_ene = []
    taux_ene = []
    gain_eau = []
    taux_eau = []
    gain = []
    taux_gain = []
    co2 = []
    taux_co2 = []
    cout = []
    taux_cout = []
    for i in tqdm(range(len(liste_solution))):
        val = calcul_cout_pondere(liste_solution['numsolution'].iloc[i])
        num_solution.append(liste_solution['numsolution'].iloc[i])
        nb_solution.append(val[10])
        gain_ene.append(round(val[0], 2))
        taux_ene.append(round(val[1], 2))
        gain_eau.append(round(val[2], 2))
        taux_eau.append(round(val[3], 2))
        gain.append(round(val[4], 2))
        taux_gain.append(round(val[5], 2))
        co2.append(round(val[6], 2))
        taux_co2.append(round(val[7], 2))
        cout.append(round(val[8], 2))
        taux_cout.append(round(val[9], 2))
    donnees = {
        "num_solution" : num_solution,
        "nb_solution" : nb_solution,
        "gain_ene" : gain_ene,
        "taux_ene" : taux_ene,
        "gain_eau" : gain_eau,
        "taux_eau" : taux_eau,
        "gain" : gain,
        "taux_gain" : taux_gain,
        "co2" : co2,
        "taux_co2" : taux_co2,
        "cout" : cout,
        "taux_cout" : taux_cout
    }
    df_donnees = pd.DataFrame(donnees)
    df_donnees.to_csv("../data/donnees_solution.csv", index=False)

# writing_csv() pour creer le csv