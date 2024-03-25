import pandas as pd

from emb import embeddings, load_embeddings
from create_collection import create_collection, query_to_sol, find_meta_ids, find_secteur







DATA_PATH_SOL = "../data/solution.csv"
DATA_PATH_SECT = "../data/secteur_solution.csv"
LANG = "french"
#MODEL_NAME = "google-bert/bert-base-multilingual-cased"
MODEL_NAME = "almanach/camembert-base"
QUERY = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
         "Comment optimiser la production de mon compresseur à air comprimé ?"]
SECTEUR = 19

#get data solution in french
df = pd.read_csv(DATA_PATH_SOL)
df_sol = df[df['codelangue'] == 2]

#get data secteur
df_sect = pd.read_csv(DATA_PATH_SECT)

# #compute embeddings
# print("Compute embeddings : ")
# list_emb = []
# i=0
# for i in tqdm(range(df.shape[0])):

#     sol = str(df.iloc[i]['titre']) + ", " + str(df.iloc[i]['definition'])
    
#     list_emb.append(embeddings(sol, MODEL_NAME, LANG))
#     # if i > 10 :
#     #     break
#     # i += 1
    

list_emb = load_embeddings("embeddings.csv")
query_emb = embeddings(QUERY[1], MODEL_NAME, LANG)


# import ast
# s = 0
# for i in range(len(df_sect)):
#     if not pd.isna(df_sect.iloc[i]["solutions"]):
#         a = ast.literal_eval(df_sect.iloc[i]["solutions"])
#         s = s + len(a)

# print(s)

#init collection
collection = create_collection(list_emb, df_sol, df_sect)

#get ids of sol
ids_filterd, ids = query_to_sol(query_emb, 33, None, 20, collection)

print(ids_filterd, ids)

print("query : ", QUERY[1])
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