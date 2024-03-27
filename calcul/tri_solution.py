import pandas as pd
import math

PRIX_KWH = 0.2516
PRIX_EAU = 0.00414

def calcul_rentabilite(liste_solutions):
    valeur = []
    df = pd.read_csv('../data/donnees_solution.csv')
    for x in liste_solutions:
        try:
            valeur.append(list(df[(df['num_solution'] == int(x))].iloc[0]))
        except:
            pass
    data = {}
    for val in valeur:
        temp = []
        if(val[10] == 0):
            cout = math.inf
        else:
            cout = round(val[10], 2)
        ratio_energetique = round((val[2] * PRIX_KWH + val[4] * PRIX_EAU) / cout, 2)
        ratio_financier = round(val[6] / cout, 2)
        ratio_co2 = round(val[8] / cout * 1000, 2)
        temp.append(ratio_energetique)
        temp.append(ratio_financier)
        temp.append(ratio_co2)
        temp.append(cout)
        temp.append(val[1])
        data[str(int(val[0]))] = temp
    return(data)

# indice 0 = ratio energetique
# indice 1 = ratio financier
# indice 2 = ratio co2
# indice 3 = cout
# indice 4 = nb application
def filtre(d, indice):
    if(indice != 3):
        sorted_d = dict(sorted(d.items(), key=lambda item: item[1][indice], reverse=True))
    else:
        sorted_d = dict(sorted(d.items(), key=lambda item: item[1][indice]))
    return(list(sorted_d.keys()))
