import pandas as pd
import math

def calcul_rentabilite(liste_solutions):
    valeur = []
    df = pd.read_csv('data/donnees_solution.csv')
    for x in liste_solutions:
        try:
            valeur.append(list(df[(df['num_solution'] == int(x))].iloc[0]))
        except:
            pass
    data = {}
    for val in valeur:
        temp = []
        if(val[8] == 0):
            cout = math.inf
        else:
            cout = round(val[8], 2)
        ratio_energetique = val[2]
        ratio_financier = val[4]
        ratio_co2 = val[6]
        taux_energetique = val[3]
        taux_financier = val[5]
        taux_co2 = val[7]
        taux_cout = val[9]
        temp.append(ratio_energetique)
        temp.append(ratio_financier)
        temp.append(ratio_co2)
        temp.append(cout)
        temp.append(val[1])
        temp.append(taux_energetique)
        temp.append(taux_financier)
        temp.append(taux_co2)
        temp.append(taux_cout)
        data[str(int(val[0]))] = temp
    return(data)

# indice 0 = ratio energetique
# indice 1 = ratio financier
# indice 2 = ratio co2
# indice 3 = cout
# indice 4 = nb application
def filtre(d, indice):
    sorted_d = dict(sorted(d.items(), key=lambda item: item[1][indice], reverse=True))
    return(list(sorted_d.keys()))
