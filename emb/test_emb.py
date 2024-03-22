import pandas as pd
from emb import embeddings, cosine_similarity, important_words


data_set = ""
LANG = "french"
MODEL_NAME = "google-bert/bert-base-multilingual-cased"
QUERY = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
         "J'aimerais avoir une régulation optimisée de mon groupe froid"]


#get data solution
df = pd.read_csv('../data.csv')
df = df[(df['typedictionnaire'] == 'sol') & (df['codelangue'] == 2)]

#embedings of all solutions : 
list_emb = []
for sol in df['texte']:
    
    list_emb.append(embeddings(sol, 20000000, MODEL_NAME, LANG))
    

    
#creat emb of query
query_emb = embeddings(MODEL_NAME, QUERY[0], LANG)

#find the best cos sim:
cos_sim = []
for emb in list_emb:
    cos_sim.append(cosine_similarity(emb, query_emb))

index_max = cos_sim.index(max(cos_sim))

print(df['text'][index_max])