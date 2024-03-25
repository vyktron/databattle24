import pandas as pd
from tqdm import tqdm
from emb import embeddings, find_answer_to_query, stock_embeddings


DATA_PATH = "../data/solution.csv"
LANG = "french"
#MODEL_NAME = "google-bert/bert-base-multilingual-cased"
MODEL_NAME = "almanach/camembert-base"
QUERY = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
         "Je veux moderniser mon compresseur pour diminuer ma consommation et économiser de l'électricité"]


#get data solution
df = pd.read_csv(DATA_PATH)
df = df[df['codelangue'] == 2]


#embedings of all solutions : 
print("Compute embeddings : ")
list_emb = []
i=0
for i in tqdm(range(df.shape[0])):

    sol = str(df.iloc[i]['titre']) + ", " + str(df.iloc[i]['definition'])
    
    list_emb.append(embeddings(sol, MODEL_NAME, LANG))
    # if i > 10 :
    #     break
    # i += 1
    

print("")

#query0
id_max_list = find_answer_to_query(QUERY[0], list_emb, 5, MODEL_NAME, LANG)
print("query : ", QUERY[0])
j = 1
for i in id_max_list:
    print("answer ", j, " : sol n", df.iloc[i]['numsolution'], " ", df.iloc[i]['titre'])
    j += 1


#query1
id_max_list = find_answer_to_query(QUERY[1], list_emb, 5, MODEL_NAME, LANG)
print("query : ", QUERY[1])
j = 1
for i in id_max_list:
    print("answer ", j, " : sol n", df.iloc[i]['numsolution'], " ", df.iloc[i]['titre'])
    j += 1


stock_embeddings(list_emb)