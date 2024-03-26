import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.extractor import Extractor
import pandas as pd

from emb.chroma_client import ChromaClient
from emb.embed import embeddings

chrclient = ChromaClient()
extractor = Extractor()

LANG = "french"
#MODEL_NAME = "google-bert/bert-base-multilingual-cased"
MODEL_NAME = "almanach/camembert-base"

df_sol_fr = extractor.extract_solution(to_csv=False)
# Keep only french solutions
df_sol_fr.reset_index(inplace=True)
# Set the index to "numsolution"
df_sol_fr.set_index("numsolution", inplace=True)
df_sol_fr = df_sol_fr[df_sol_fr['codelangue'] == 2]

#function who return a dictionnary with name and code of the sector
def get_sectors():
    sec=extractor.extract_sectors(to_csv=False)
    df_sol_rex = extractor.extract_solution_rex(to_csv=False)
    s_sec=extractor.extract_sector_solution(df_sol_rex, to_csv=False)

    list_name=[]
    list_s_sec=s_sec["sous_secteurs"][1]

    #Keep only sectors line in fr (i.e codelangue=2)
    sec_fr=sec[sec['codelangue']==2]

    for i in range(1, len(list_s_sec)):
        # Get the "titre" of the sector
        num = list_s_sec[i]
        # "num" is the index of the sector in the dataframe
        # Get the "titre" of the sector
        name = sec_fr.loc[num, "titre"]
        list_name.append({"name":name, "code":num})

        sub_secteurs = s_sec["sous_secteurs"][num]
        list_name[i-1]["sub_secteurs"] = []
        for sub in sub_secteurs:
            name = sec_fr.loc[sub, "titre"]
            list_name[i-1]["sub_secteurs"].append({"name":name, "code":sub})

    return list_name

def find_best_solutions(query : str, ssect : int, sect : int, nb_sol : int):

    # Get the embeddings of the query
    query_emb = embeddings(query, MODEL_NAME, LANG)
    # Get the ids of the n-th first solutions filtered by the sub-sector and the sector (and nothing)
    ids_ssec_filtered, ids_sect_filtered, ids = chrclient.query_to_sol(query_emb, sect, ssect, nb_sol)
    # Sort the solutions by score
    return chrclient.sort_by_score(ids_ssec_filtered, ids_sect_filtered, ids)

def get_solution_info_by_id(id_sol : int):

    sol_title = df_sol_fr.loc[id_sol]["titre"]
    return sol_title

def get_solutions_info_by_id(ids : list) -> dict:

    solutions = []
    for i in ids:
        solutions.append({"code":i, "title":get_solution_info_by_id(int(i))})

    return solutions

# x=get_name()
# print(x)