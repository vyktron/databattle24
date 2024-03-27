#import
import chromadb
import ast
import pandas as pd



def find_sous_secteurs(df, sol):

    #get all sous_secteur
    df_ss = df[df['sous_secteurs'].isnull()]

    s_secteur = []

    #find the ss of the solution
    for i in range(len(df_ss)):
        if not pd.isna(df_ss.iloc[i]["solutions"]):
            sect = df_ss.iloc[i]['numsecteur']
            if sol in ast.literal_eval(df_ss.iloc[i]['solutions']) and sect not in s_secteur:
                s_secteur.append(sect)

    return s_secteur


def find_secteur(df, s_secteur):

    #get all secteur:
    df_s = df.dropna(subset=['sous_secteurs'])

    secteur = []

    #find is there are a grandparent
    for j in range(len(s_secteur)):
        secteur.append(s_secteur[j])
        for i in range(len(df_s)):
            if s_secteur[j] in ast.literal_eval(df_s.iloc[i]['sous_secteurs']):
                secteur[j] = df_s.iloc[i]['numsecteur']

    return secteur


def find_techno_by_sub(df, s_techno, test):

    if s_techno == 1:
        return test
    else:
        for i in range(len(df)):
            if s_techno in ast.literal_eval(df.iloc[i]['sous_techno']):
                techno = df.iloc[i]['numtechno']
                return find_techno_by_sub(df, techno, s_techno)
                
        return s_techno


def find_grand_techno(df, sol):

    #find sub_techno
    df_st = df[df['sous_techno'].isnull()]

    s_techno = "null"
    for i in range(len(df_st)):
        if not pd.isna(df_st.iloc[i]["solutions"]):
            if sol in ast.literal_eval(df_st.iloc[i]['solutions']):
                s_techno = df_st.iloc[i]['numtechno']

    #find grand techno
    if s_techno != "null":
        df_t = df.dropna(subset=['sous_techno'])
        techno = find_techno_by_sub(df_t, s_techno, s_techno)

        return techno

    else:
        return s_techno



#return metadata
#return ids as str (numsolution)
def find_meta_ids(list_emb, df_sol, df_sect, df_tech):

    metadata = []
    ids = []
    
    for i in range(len(list_emb)):

        #initalise metadata to 0
        meta = {}
        for j in range(60):
            meta['secteur'+str(j)] = 0

        sol = df_sol.iloc[i]['numsolution']
        s_secteur = find_sous_secteurs(df_sect, sol)
        secteur = find_secteur(df_sect, s_secteur)

        for sect in secteur:
            meta['secteur'+str(sect)] = 1
        for s_sect in s_secteur:
            meta['sous_secteur'+str(s_sect)] = 1

        #add grand technology metadata
        techno = find_grand_techno(df_tech, sol)
        meta['techno'] = str(techno)

        ids.append(str(sol))
        metadata.append(meta)

    return metadata, ids



#list of all embeddings
#dataset of all solution in french
#dataset of all secteur
def create_collection(list_emb, df_sol, df_sect, df_tech):

    client = chromadb.Client()
    collection = client.create_collection("embeddings")

    metadatas, ids = find_meta_ids(list_emb, df_sol, df_sect, df_tech)
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
def query_to_sol(query_emb, collection, secteur=None, sous_secteur=None, techno=None, n_res=10):

    if secteur == None:
        secteur = ""
    if sous_secteur == None:
        sous_secteur = ""


    res_ssect = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res,
        where={
            "sous_secteur" + str(sous_secteur): 1
        }
    )

    res_sect = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res,
        where={
            "secteur" + str(secteur): 1
        }
    )

    res_techno = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res,
        where={
            "techno": str(techno)
        }
    )

    res = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=n_res
    )

    return res_ssect['ids'][0], res_sect['ids'][0], res_techno['ids'][0], res['ids'][0]



#return ids of sol with the best score
def sort_by_score(res_ssect, res_sect, res_techno, res):

    #score_map {'id': score}
    score_map = {}

    i = 0.9
    for res_l in [res_techno, res_sect, res, res_ssect]:
        i += 0.1
        for r in res_l:
            s = len(res)/i
            if  r in score_map:
                score_map[r] = score_map[r] + s
            else:
                score_map[r] = s

    return sorted(score_map.keys(), key=score_map.get, reverse=True)[:len(res)]