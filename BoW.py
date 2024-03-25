# import
from sklearn.feature_extraction.text import CountVectorizer
# import nltk
# from nltk.corpus import stopwords
import pandas as pd

def BoW(new_sentence, langue):
    df = pd.read_csv('data.csv')
    liste_tech = df[(df['typedictionnaire'] == 'tec') & (df['1'])]

    technologies = []
    for phrase in liste_tech["1"]:
        technologies.append(str(phrase))

    vectorizer = CountVectorizer()
    X_train = vectorizer.fit_transform(technologies)
    entrainement = X_train.toarray()

    new_sentence_bow = vectorizer.transform([new_sentence])
    calc = new_sentence_bow.toarray()

    result = []
    for j in range(len(entrainement)):
        val = 1
        for i in range(len(entrainement[j])):
            if entrainement[j][i] == 1 and calc[0][i] == 0:
                val = 0
        if(val == 1):
            result.append(j)

    tech_reliees = []
    if(result != []):
        for x in result:
            tech_reliees.append(technologies[x])
    else:
        return []

    tech_reliees = set(tech_reliees)

    if(len(tech_reliees) > 1):
        return(tech_reliees)

    num_tech = []

    for x in tech_reliees:
        num_tech.append(df[(df['typedictionnaire'] == 'tec') & (df['1'] == x)]["codeappelobjet"])

    solutions = []
    df_sol = pd.read_csv('solution_techno.csv')
    for x in num_tech:
        cles = x.keys()
        for k in cles:
            solutions.append(df_sol[(df_sol['codetechno'] == int(x[k]))]["numsolution"])

    print("\n")
    solutions_final = []
    for x in solutions:
        keys = x.keys()
        for k in keys:
            temp = x[k][1:-1]
            liste_solution = temp.split(",")
            for j in liste_solution:
                sol_temp = df[(df['typedictionnaire'] == 'sol') & (df['codeappelobjet'] == int(j)) & (df["codelangue"] == int(langue))]
                i = 1
                fin = False
                while(not fin):
                    for x in sol_temp[str(i)]:
                        if pd.isna(x):
                            fin = True
                        else:
                            solutions_final.append(x)
                            i += 1
    return(solutions_final)


# new_sentence = "J'aimerais avoir une aide au management (ISO 50 001)"
new_sentence = "Comment faire pour réduire la consommation du groupe froid de mon compresseur d'air comprimé ?"
techs = list(BoW(new_sentence, 2))
for x in techs:
    print(x)