# import
from sklearn.feature_extraction.text import CountVectorizer
# import nltk
# from nltk.corpus import stopwords
import pandas as pd
import joblib

def BoW_csv(langue):
    df = pd.read_csv('./data/technologie.csv')
    liste_tech = df[(df['codelangue'] == int(langue)) & (df['titre'])]

    technologies = []
    for phrase in liste_tech["titre"]:
        technologies.append(str(phrase))

    vectorizer = CountVectorizer()
    X_train = vectorizer.fit_transform(technologies)
    entrainement = X_train.toarray()
    joblib.dump((vectorizer, entrainement), 'BoW.joblib')

    # df_Bow = pd.DataFrame(entrainement)
    # df_Bow.to_csv("BoW.csv", index=False)


def lien_Bow(new_sentence, langue):

    df = pd.read_csv('BoW.csv')
    entrainement = []
    for i in range(len(df)):
        entrainement.append(list(df.iloc[i]))

    vectorizer, entrainement = joblib.load('BoW.joblib')
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
    df = pd.read_csv('./data/technologie.csv')
    liste_tech = df[(df['codelangue'] == int(langue)) & (df['titre'])]
    if(result != []):
        for x in result:
            tech_reliees.append(liste_tech[(liste_tech["numtechnologie"] == x + 2)]["titre"].iloc[0])
    else:
        return []

    tech_reliees = set(tech_reliees)

    return(tech_reliees)

# new_sentence = "J'aimerais avoir une aide au management (ISO 50 001)"
new_sentence = "Panneau solaire"
BoW_csv(2)
techs = list(lien_Bow(new_sentence, 2))
for x in techs:
    print(x)