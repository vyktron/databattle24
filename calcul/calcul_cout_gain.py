# import
from tqdm import tqdm
import pandas as pd

PRIX_KWH = 0.2516
PRIX_EAU = 0.00414

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

def calcul_cout_pondere(num_solution):
    df_soluce = pd.read_csv('./data/solution_rex.csv')
    df_monnaie = pd.read_csv('./data/monnaie.csv')
    liste_soluce = df_soluce[(df_soluce['numsolution'] == int(num_solution))]

    conso = 0
    cout_conso = 0
    nb_conso = 0

    gain = 0
    cout_gain = 0
    nb_gain = 0

    co2 = 0
    cout_co2 = 0
    nb_co2 = 0
    
    cout = 0
    nb_cout = 0

    for i in range(len(liste_soluce)):

        presence_cout = 0

        if(not pd.isna(liste_soluce["reel_cout"].iloc[i]) and liste_soluce["reel_cout"].iloc[i] != 0):
            presence_cout = conversion(liste_soluce["reel_cout"].iloc[i], liste_soluce["code_monnaie_cout"].iloc[i], df_monnaie)
            nb_cout += 1
        elif((not pd.isna(liste_soluce["mini_cout"].iloc[i]) and liste_soluce["mini_cout"].iloc[i] != 0) and (not pd.isna(liste_soluce["maxi_cout"].iloc[i]) and liste_soluce["maxi_cout"].iloc[i] != 0)):
            cout_temp = (liste_soluce["mini_cout"].iloc[i] + liste_soluce["maxi_cout"].iloc[i]) / 2
            presence_cout = conversion(cout_temp, liste_soluce["code_monnaie_cout"].iloc[i], df_monnaie)
            nb_cout += 1
        cout += presence_cout

        if(presence_cout != 0):
            
            if(not pd.isna(liste_soluce["energie_gain"].iloc[i])):
                tempo = conversion_conso(i, liste_soluce)
                if(tempo[1] != -1):
                    if(tempo[1] == 1):
                        conso += tempo[0] * PRIX_EAU
                    else:
                        conso += tempo[0] * PRIX_KWH
                    nb_conso += 1
                    cout_conso += presence_cout

            if(not pd.isna(liste_soluce["gain"].iloc[i])):
                gain += conversion(liste_soluce["gain"].iloc[i], liste_soluce["code_monnaie_gain"].iloc[i], df_monnaie)
                nb_gain += 1
                cout_gain += presence_cout
                
            if(not pd.isna(liste_soluce["ges_gain"].iloc[i])):
                co2 = liste_soluce["ges_gain"].iloc[i]
                nb_co2 += 1
                cout_co2 += presence_cout
    
    if(len(liste_soluce) != 0):
        taux_conso = round(nb_conso / len(liste_soluce) * 100, 2)
        taux_gain = round(nb_gain / len(liste_soluce) * 100, 2)
        taux_co2 = round(nb_co2 / len(liste_soluce) * 100, 2)
        taux_cout = round(nb_cout / len(liste_soluce) * 100, 2)
    else:
        taux_conso = 0
        taux_gain = 0
        taux_co2 = 0
        taux_cout = 0

    if(nb_conso != 0):
        gain_conso = conso / cout_conso
    else:
        gain_conso = 0

    if(nb_gain != 0):
        gain = gain / cout_gain
    else:
        gain = 0

    if(nb_co2 != 0):
        gain_co2 = co2 / cout_co2
    else:
        gain_co2 = 0

    if(nb_cout != 0):
        cout = cout / nb_cout
    else:
        gain_co2 = 0
    
    return([gain_conso, taux_conso, gain, taux_gain, gain_co2, taux_co2, cout, taux_cout, len(liste_soluce)])

def writing_csv():
    df_solution = pd.read_csv('./data/solution.csv')
    liste_solution = df_solution[(df_solution['codelangue'] == int(2))]
    num_solution = []
    nb_solution = []
    gain_conso = []
    taux_conso = []
    gain = []
    taux_gain = []
    gain_co2 = []
    taux_co2 = []
    cout = []
    taux_cout = []
    for i in tqdm(range(len(liste_solution))):
        val = calcul_cout_pondere(liste_solution['numsolution'].iloc[i])
        num_solution.append(liste_solution['numsolution'].iloc[i])
        nb_solution.append(val[8])
        gain_conso.append(round(val[0], 2))
        taux_conso.append(round(val[1], 2))
        gain.append(round(val[2], 2))
        taux_gain.append(round(val[3], 2))
        gain_co2.append(round(val[4], 2))
        taux_co2.append(round(val[5], 2))
        cout.append(round(val[6], 2))
        taux_cout.append(round(val[7], 2))
    donnees = {
        "num_solution" : num_solution,
        "nb_solution" : nb_solution,
        "gain_conso" : gain_conso,
        "taux_conso" : taux_conso,
        "gain" : gain,
        "taux_gain" : taux_gain,
        "gain_co2" : gain_co2,
        "taux_co2" : taux_co2,
        "cout" : cout,
        "taux_cout" : taux_cout
    }
    df_donnees = pd.DataFrame(donnees)
    df_donnees.to_csv("./data/donnees_solution.csv", index=False)

writing_csv()
