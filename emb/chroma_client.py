# Import
import chromadb
from chromadb.config import Settings
import ast
import pandas as pd

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
from db.extractor import Extractor
from emb.embed import load_embeddings

class ChromaClient:
    def __init__(self, reset : bool = False):
        self.client = chromadb.HttpClient(host="0.0.0.0", port=8001, settings=Settings(allow_reset=True, anonymized_telemetry=False))

        self.embeddings_path = "emb/chromadb/embeddings.csv"
        self.lang = 2 # french

        self.collection = None
        self.collection_name = "embeddings"
        self.build_collection(reset)

    def show_collection(self):
        if self.collection :
            print("Collection \'" + self.collection.name + "\' with " + str(self.collection.count()) + " elements")

    def find_sub_sector(self, df, sol):
        # get all sub_sectors
        df_ss = df[df['sous_secteurs'].isnull()]
        s_secteur = []

        # find the sub-sectors of the solution
        for i in range(len(df_ss)):
            if not isinstance(df_ss.iloc[i]["solutions"], float): # check if the value is not NaN => float
                sect = df_ss.iloc[i]['numsecteur']
                if sol in df_ss.iloc[i]['solutions'] and sect not in s_secteur:
                    s_secteur.append(sect)

        return s_secteur

    def find_sector(self, df, s_secteur):
        # get all secteur:
        df_s = df.dropna(subset=['sous_secteurs'])
        secteur = []

        #find is there are a grandparent
        for j in range(len(s_secteur)):
            secteur.append(s_secteur[j])
            for i in range(len(df_s)):
                if s_secteur[j] in df_s.iloc[i]['sous_secteurs']:
                    secteur[j] = df_s.iloc[i]['numsecteur']

        return secteur
    
    def find_techno_by_sub(self, df, s_techno, test):

        if s_techno == 1:
            return test
        else:
            for i in range(len(df)):
                if s_techno in df.iloc[i]['sous_techno']:
                    techno = df.iloc[i]['numtechno']
                    return self.find_techno_by_sub(df, techno, s_techno)
                    
        return s_techno
    
    def find_grand_techno(self, df, sol):

        #find sub_techno
        df_st = df[df['sous_techno'].isnull()]

        s_techno = "null"
        for i in range(len(df_st)):
            if not isinstance(df_st.iloc[i]["solutions"], float):
                if sol in df_st.iloc[i]['solutions']:
                    s_techno = df_st.iloc[i]['numtechno']

        #find grand techno
        if s_techno != "null":
            df_t = df.dropna(subset=['sous_techno'])
            techno = self.find_techno_by_sub(df_t, s_techno, s_techno)

            return techno

        else:
            return s_techno

    def find_meta_ids(self, list_emb, df_sol, df_sect, df_tech):
        metadata = []
        ids = []
        
        for i in range(len(list_emb)):

            #initalise metadata to 0
            meta = {}
            for j in range(2,60):
                meta['sec'+str(j)] = 0

            sol = df_sol.iloc[i]['numsolution']
            s_secteur = self.find_sub_sector(df_sect, sol)
            secteur = self.find_sector(df_sect, s_secteur)

            for sect in secteur:
                meta['sec'+str(sect)] = 1
            for s_sect in s_secteur:
                meta['sec'+str(s_sect)] = 1
            
            #add grand technology metadata
            techno = self.find_grand_techno(df_tech, sol)
            meta['techno'] = str(techno)

            ids.append(str(sol))
            metadata.append(meta)

        return metadata, ids

    def build_collection(self, reset : bool):
        """
        Build the collection with the embeddings
        If reset is True, the collection is emptied and recreated
        
        Parameters:
        reset : bool
            If True, the collection is emptied and recreated
        """
        
        # Empty the collection
        if len(self.client.list_collections()) > 0 and self.collection_name in [c.name for c in self.client.list_collections()]:
            if not reset:
                self.collection = self.client.get_collection(self.collection_name)
                print("Collection already exists, skipping creation.")
                return
            self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(self.collection_name)

        print("Building collection...")

        extractor = Extractor()
        # Load the embeddings
        list_emb = load_embeddings(self.embeddings_path)
        # Load the solutions
        df_sol = extractor.extract_solution(to_csv=False)
        df_sol.reset_index(inplace=True)
        df_sol = df_sol[df_sol["codelangue"] == self.lang]        
        # Load the sectors
        df_sect = extractor.extract_sector_solution(extractor.extract_solution_rex(to_csv=False), to_csv=False)
        df_sect.reset_index(inplace=True)

        df_tech_sol = extractor.extract_techno_solution(to_csv=False)
        df_tech_sol.reset_index(inplace=True)

        # Add the embeddings to the collection
        metadatas, ids = self.find_meta_ids(list_emb, df_sol, df_sect, df_tech_sol)

        self.collection.add(
            embeddings=list_emb,
            metadatas=metadatas,
            ids=ids,
        )

        print("Created :", end=" ") ; self.show_collection()


    #query as embeddings
    #secteur, sous_secteur as string
    #n_res int
    #collection is chromadb collection
    #return list of n_res ids filtered and not
    def query_to_sol(self, query_emb, secteur=None, sous_secteur=None, techno=None, n_res=10):
        print("techno : ", techno)
        if secteur == None:
            secteur = ""
        if sous_secteur == None:
            sous_secteur = ""
        if techno == None:
            techno = ""

        res_ssect = {"ids": [[]]} ; res_sect = {"ids": [[]]} ; res_techno = {"ids": [[]]}

        if sous_secteur != "":
            res_ssect = self.collection.query(
                query_embeddings=query_emb.tolist(),
                n_results=n_res,
                where={
                    "sec" + str(sous_secteur): 1
                }
            )
        
        if secteur != "":
            res_sect = self.collection.query(
                query_embeddings=query_emb.tolist(),
                n_results=n_res,
                where={
                    "sec" + str(secteur): 1
                }
            )

        if techno != "":
            res_techno = self.collection.query(
                query_embeddings=query_emb.tolist(),
                n_results=n_res,
                where={
                    "techno": str(techno)
                }
            )

        res = self.collection.query(
            query_embeddings=query_emb.tolist(),
            n_results=n_res
        )

        return res_ssect['ids'][0], res_sect['ids'][0], res_techno['ids'][0], res['ids'][0]
    
    #return ids of sol with the best score
    def sort_by_score(self, res_ssect, res_sect, res_techno, res):

        #score_map {'id': score}
        score_map = {}

        print("Results : ", res_ssect, res_sect, res_techno, res)

        i = 0.75
        for res_ in [res_techno, res_sect, res, res_ssect]:
            i += 0.25
            for j, r in enumerate(res_):
                s = (len(res)-j)/i
                if  r in score_map:
                    score_map[r] = score_map[r] + s
                else:
                    score_map[r] = s

        print("Score map : " + str(score_map))
        print(sorted(score_map.keys(), key=score_map.get, reverse=True)[:len(res)])
        return sorted(score_map.keys(), key=score_map.get, reverse=True)[:len(res)]

if __name__ == "__main__":
    # Test
    chroma = ChromaClient(reset=True)
    chroma.show_collection()

    # Get element id 720
    print(chroma.collection.get(ids=["282"], include=["embeddings", "metadatas"]))