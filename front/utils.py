import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.extractor import Extractor
import pandas as pd

extractor = Extractor()



#function who return a dictionnary with name and code of the sector
def get_name():
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

x=get_name()
print(x)