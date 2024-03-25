#import
import chromadb
import ast
import pandas as pd



def find_sous_secteurs(df, sol):

    #get all sous_secteur
    df_ss = df[df['sous_secteurs'].isnull()]

    s_secteur = "null"

    #find the ss of the solution
    for i in range(len(df_ss)):
        if not pd.isna(df_ss.iloc[i]["solutions"]):
            if sol in ast.literal_eval(df_ss.iloc[i]['solutions']):
                s_secteur = df_ss.iloc[i]['numsecteur']

    return s_secteur


def find_secteur(df, s_secteur):

    #get all secteur:
    df_s = df.dropna(subset=['sous_secteurs'])

    secteur = s_secteur

    #find is there are a grandparent
    for i in range(len(df_s)):
        if s_secteur in ast.literal_eval(df_s.iloc[i]['sous_secteurs']):
            secteur = df_s.iloc[i]['numsecteur']
                
    return secteur



#return metadata
#return ids as str (numsolution)
def find_meta_ids(list_emb, df_sol, df_sect):

    metadata = []
    ids = []
    for i in range(len(list_emb)):
        
        sol = df_sol.iloc[i]['numsolution']
        s_secteur = find_sous_secteurs(df_sect, sol)
        secteur = find_secteur(df_sect, s_secteur)

        meta = {
            "secteur": str(secteur),
            "sous_secteur": str(s_secteur)
        }

        ids.append(str(sol))
        metadata.append(meta)
    
    return metadata, ids



#list of all embeddings
#dataset of all solution in french
#dataset of all secteur
def create_collection(list_emb, df_sol, df_sect):

    client = chromadb.Client()
    collection = client.create_collection("embeddings")

    metadatas, ids = find_meta_ids(list_emb, df_sol, df_sect)
    collection.add(
        embeddings=list_emb,
        metadatas=metadatas,
        ids=ids,
    )

    return collection


#query as embeddings
#secteur, sous_secteur as string
#n_res int
#collection is chromadb collection
#return list of n_res ids filtered and not
def query_to_sol(query_emb, secteur, sous_secteur, n_res, collection):

    res_filterd = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res,
        where={
            "secteur": str(secteur)
            #"sous_secteur": str(sous_secteur)
        }
    )

    res = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res
    )

    return res_filterd['ids'][0], res['ids'][0]