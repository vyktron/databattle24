#clustering for embbedings

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
from tqdm import tqdm
import numpy as np
import ast

import sys
sys.path.append('../')
from emb.emb import embeddings

DATA_PATH_DICO = "../data/dictionary.csv"
DATA_PATH_TECH = "../data/techno_solution.csv"

LANG = "french"
#MODEL_NAME = "google-bert/bert-base-multilingual-cased"
MODEL_NAME = "almanach/camembert-base"
QUERY = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
         "J'aimerais avoir une régulation optimisée de mon groupe froid"]


#get data solution
df = pd.read_csv(DATA_PATH_DICO)
df = df[(df['typedictionnaire'] == 'sol') & (df['codelangue'] == 2)]

df2 = pd.read_csv(DATA_PATH_TECH)
df2 = df2[df2['child_techno'].isnull()]

#embedings of all solutions : 
print("Compute embeddings : ")
list_emb = []
i=0
for sol in tqdm(df['1']):
    
    list_emb.append(embeddings(sol, 512, MODEL_NAME, LANG))
    if i > 10 :
        break
    i += 1


list_emb = np.concatenate([emb.numpy().reshape(1, -1) for emb in list_emb])


# Define number of clusters (K)
k = 3

# Apply K-means clustering
kmeans = KMeans(n_clusters=k, n_init='auto')
kmeans.fit(list_emb)

predictions = kmeans.predict(list_emb)
L = [[] for x in range(k)]
for i in range(len(list_emb)):

    #solution in cluster
    numsol = df.iloc[i]['codeappelobjet']
    for j in range(len(df2)):
        
        if numsol in ast.literal_eval(df2.iloc[j]['numsolution']):
            numtechno = df2.iloc[j]['numtechno']

    L[predictions[i]].append((numsol, numtechno))


print(L)





# Get cluster labels and centroids
cluster_labels = kmeans.labels_

# Plot data points
plt.scatter(list_emb[:, 0], list_emb[:, 1], c=cluster_labels, cmap='viridis', alpha=0.5, label='Data Points')


plt.title('Embeddings K-means Clustering')
# plt.xlabel('Feature 1')
# plt.ylabel('Feature 2')
# plt.legend()
plt.grid(True)
plt.show()