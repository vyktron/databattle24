import pandas as pd
from tqdm import tqdm

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emb.embed import embeddings, load_embeddings, stock_embeddings
from chroma_client import ChromaClient



DATA_PATH_SOL = "data/solution.csv"
DATA_PATH_SECT = "data/secteur_solution.csv"
LANG = "french"
#MODEL_NAME = "google-bert/bert-base-multilingual-cased"
MODEL_NAME = "almanach/camembert-base"
QUERY = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
         "Comment optimiser la production de mon compresseur à air comprimé ?",
         "Je voudrais dimensionner un panneau solaire",
         "C'est quoi la HP flottante ?",
         "Quel gain pour un variateur de vitesse ?"]
SECTEUR = 19

#get data solution in french
df = pd.read_csv(DATA_PATH_SOL)
df_sol = df[df['codelangue'] == 2]

#get data secteur
df_sect = pd.read_csv(DATA_PATH_SECT)

#compute embeddings
#print("Compute embeddings : ")
#list_emb = []
#i=0
#for i in tqdm(range(df_sol.shape[0])):
    
#    sol = str(df.iloc[i]['titre']) + ", " + str(df.iloc[i]['definition'])

#    list_emb.append(embeddings(sol, MODEL_NAME, LANG))
#    # if i > 10 :
#    #     break
#    # i += 1
    
# Store embeddings
# stock_embeddings(list_emb)
#list_emb = load_embeddings("emb/chromadb/embeddings.csv")
query_emb = embeddings(QUERY[4], MODEL_NAME, LANG)


# import ast
# s = 0
# for i in range(len(df_sect)):
#     if not pd.isna(df_sect.iloc[i]["solutions"]):
#         a = ast.literal_eval(df_sect.iloc[i]["solutions"])
#         s = s + len(a)

# print(s)

chclient = ChromaClient()

#get ids of sol
ids_filterd, ids = chclient.query_to_sol(query_emb, 9, 12, 20)

print(ids_filterd, ids)

print("query : ", QUERY[4])
j = 1
for i in ids:
    i = int(i)
    print("answer ", j, " : sol n" + str(i) + " ", df_sol.loc[df_sol['numsolution'] == i, 'titre'].values[0])
    j += 1

j = 1
for i in ids_filterd:
    i = int(i)
    print("answer filtered ", j, " : sol n" + str(i) + " ", df_sol.loc[df_sol['numsolution'] == i, 'titre'].values[0])
    j += 1