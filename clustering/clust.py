#clustering for embbedings

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import pandas as pd
from tqdm import tqdm
import numpy as np
import ast
from collections import Counter

import sys
sys.path.append('../')
from emb.emb import embeddings, load_embeddings

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

df1 = pd.read_csv(DATA_PATH_TECH)
df2 = df1[df1['child_techno'].isnull()]

print(df2.shape)

#get embeddigns
list_emb = load_embeddings("../emb/embeddings.csv")




def find_grand_parent(df, techno):

    row = df[df['numtechno'] == techno]

    if row['child_techno'].isna().values[0]:

        for i in range(len(df)):

            if not pd.isna(df.iloc[i]['child_techno']):
                if techno in ast.literal_eval(df.iloc[i]['child_techno']):
                    return df.iloc[i]['numtechno']

    else:
        return techno
    





#list_emb = np.concatenate([emb.numpy().reshape(1, -1) for emb in list_emb])


# Define number of clusters (K)
k = 179

# Apply K-means clustering
kmeans = KMeans(n_clusters=k, n_init='auto')
kmeans.fit(list_emb)

predictions = kmeans.predict(list_emb)
L = [[] for x in range(k)]




# tmp = list_emb
# import random
# import time
# current_time = int(time.time())

# # Set the random seed using the current timestamp
# random.seed(current_time)
# while tmp != []:
#     j = random.randint(0,len(tmp)-1)
#     L[random.randint(0,178)].append(tmp[j])
#     tmp.pop(j)
    


for i in range(len(list_emb)):

    #solution in cluster
    numsol = df.iloc[i]['codeappelobjet']
    for j in range(len(df2)):
        
        if numsol in ast.literal_eval(df2.iloc[j]['numsolution']):
            numtechno = df2.iloc[j]['numtechno']

            num_gp_techno = find_grand_parent(df1, numtechno)

    #(solution, techno)
    L[predictions[i]].append((numsol, num_gp_techno))

print(L)


bien_classe = 0
mal_classe = 0
#for all cluster, find te most present techno
for l in L:
    counts = Counter(item[1] for item in l)
    cluster_techno = max(counts, key=counts.get)
    print(cluster_techno)
    for i in range(len(l)):
        if l[i][1] == cluster_techno:
            bien_classe += 1
        else:
            mal_classe += 1

acc = bien_classe / (bien_classe + mal_classe)
print("bien_classe : ", bien_classe)
print("mal_classe : ", mal_classe)
print("accuracy = ", acc)



# from sklearn.decomposition import PCA
# #return new list_emb and print
# def compute_PCA(list_emb):
#     pca = PCA(n_components=2)
#     list_emb_PCA = pca.fit_transform(list_emb)

#     plt.subplot(1, 2, 2)
#     plt.scatter(list_emb_PCA[:, 0], list_emb_PCA[:, 1], alpha=0.8)
#     plt.xlabel('Principal Component 1')
#     plt.ylabel('Principal Component 2')
#     plt.title('Data along Principal Components')

#     plt.tight_layout()
#     plt.show()


# # Get cluster labels and centroids
# cluster_labels = kmeans.labels_

# # Plot data points
# plt.scatter(list_emb[:, 0], list_emb[:, 1], c=cluster_labels, cmap='viridis', alpha=0.5, label='Data Points')


# plt.title('Embeddings K-means Clustering')
# # plt.xlabel('Feature 1')
# # plt.ylabel('Feature 2')
# # plt.legend()
# plt.grid(True)
# plt.show()

