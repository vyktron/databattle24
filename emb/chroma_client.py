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
        s_secteur = "null"

        # Find the sub_sector of the solution
        for i in range(len(df_ss)):
            if not isinstance(df_ss.iloc[i]["solutions"], float):
                if sol in df_ss.iloc[i]['solutions']:
                    s_secteur = df_ss.iloc[i]['numsecteur']

        return s_secteur

    def find_sector(self, df, s_secteur):
        # get all secteur:
        df_s = df.dropna(subset=['sous_secteurs'])
        secteur = s_secteur

        # find if there are a grandparent
        for i in range(len(df_s)):
            if s_secteur in df_s.iloc[i]['sous_secteurs']:
                secteur = df_s.iloc[i]['numsecteur']

        return secteur

    def find_meta_ids(self, list_emb, df_sol, df_sect):
        metadatas = []
        ids = []
        for i in range(len(list_emb)):
            sol = df_sol.iloc[i]['numsolution']
            s_secteur = self.find_sub_sector(df_sect, sol)
            secteur = self.find_sector(df_sect, s_secteur)

            meta = {
                "secteur": str(secteur),
                "sous_secteur": str(s_secteur)
            }

            ids.append(str(sol))
            metadatas.append(meta)

        return metadatas, ids

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

        # Add the embeddings to the collection
        metadatas, ids = self.find_meta_ids(list_emb, df_sol, df_sect)

        self.collection.add(
            embeddings=list_emb,
            metadatas=metadatas,
            ids=ids,
        )

        print("Created :", end=" ") ; self.show_collection()


    def query_to_sol(self, query_emb, secteur, sous_secteur, n_res):

        # TODO: Filter the results by sector and sub-sector take care of None values
        res_filtered = self.collection.query(
            query_embeddings=query_emb.tolist(),
            n_results=n_res,
            where={
                "$and": [
                    {"secteur": str(secteur)},
                    {"sous_secteur": str(sous_secteur)}
                ]
            }
        )
        res = self.collection.query(
            query_embeddings=query_emb.tolist(),
            n_results=n_res
        )

        return res_filtered['ids'][0], res['ids'][0]

if __name__ == "__main__":
    # Test
    chroma = ChromaClient(reset=True)
    chroma.show_collection()

    # Get element id 720
    print(chroma.collection.get(ids=["720"], include=["embeddings", "metadatas"]))