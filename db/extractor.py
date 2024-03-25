import mysql.connector
import pandas as pd
import re
from html import unescape
import requests

class Extractor:
    """
    This class is used to extract data from the database
    """

    def __init__(self):
        self.cnx = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="user",
            password="password",
            database="kerdos"
        )
        self.cursor = self.cnx.cursor()
        self.output_path = "data"

    def extract_dictionnaire(self, type : str="sol", table_name : str="solution", to_csv : bool=True) -> pd.DataFrame:
        """
        Extract data from tbldictionnaire table and save it to a CSV file
        More precisely, we extract the columns "typedictionnaire", "codeappelobjet", "codelangue", "indexdictionnaire", and the associated "texte"
        and save it to a CSV file

        Parameters:
        -----------
            type (str): The type of dictionnary to extract. Can be "sol" for solutions, "tec" for technologies, "sec" for sectors, etc.
            table_name (str): The name of the table to save the data to (in CSV format or in a database table)
        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        CSV_FILENAME = table_name + ".csv"

        # Select all rows where typedictionnaire is either "sol" or "tec"
        self.cursor.execute("SELECT * FROM tbldictionnaire WHERE typedictionnaire = %s", (type,))
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["id", "codelangue", "typedictionnaire", "num"+table_name, "indexdictionnaire", "texte"])

        # Remove HTML tags and unescape HTML entities
        df["texte"] = df["texte"].apply(lambda x: re.sub(r"<[^>]*>", "", x))
        df["texte"] = df["texte"].apply(lambda x: unescape(x))

        # Pivot table to have one row per (typedictionnaire, codeappelobjet, codelangue) combination
        pivot_df = df.pivot_table(index=["num"+table_name, "codelangue"], columns="indexdictionnaire", values="texte", aggfunc=lambda x: ' '.join(x))
        
        # Rename the columns "1" into "titre" and "2" into "definition", "5" into "application"
        pivot_df.rename(columns={1: "titre", 2: "definition", 5: "application"}, inplace=True)

        # Save the result to a CSV file
        if to_csv:
            pivot_df.to_csv(self.output_path + "/" + CSV_FILENAME)
        return pivot_df
    
    def extract_dictionnaire_categories(self, type : str="uni", table_name : str="unite", to_csv : bool=True) -> pd.DataFrame:
        """
        Extract data from tbldictionnairecategories table and save it to a CSV file
        More precisely, we extract the columns "typedictionnairecategories", "codeappelobjet", "codelangue", "indexdictionnairecategories", and the associated "texte"
        and save it to a CSV file

        Parameters:
        -----------
            type (str): The type of dictionnary to extract. Can be "uni" for units, "per" for periods, "mon" for currencies, etc.
            table_name (str): The name of the table to save the data to (in CSV format or in a database table)
        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        CSV_FILENAME = table_name + ".csv"

        # Select all rows where typedictionnairecategories is either "uni" or "per"
        self.cursor.execute("SELECT * FROM tbldictionnairecategories WHERE typedictionnairecategories = %s AND indexdictionnairecategories=1", (type,))
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["id", "codelangue", "typedictionnairecategories", "codeappelobjet", "indexdictionnairecategories", "traductiondictionnairecategories"])

        # Keep only the columns "codeappelobjet" and "codelangue" and "traductiondictionnairecategories"
        df = df[["codeappelobjet", "codelangue", "traductiondictionnairecategories"]]

        # Remove HTML tags and unescape HTML entities
        df["traductiondictionnairecategories"] = df["traductiondictionnairecategories"].apply(lambda x: re.sub(r"<[^>]*>", "", x))
        df["traductiondictionnairecategories"] = df["traductiondictionnairecategories"].apply(lambda x: unescape(x))

        # Set the index to "codeappelobjet" and "codelangue"
        df.set_index(["codeappelobjet", "codelangue"], inplace=True)

        if to_csv:
            df.to_csv(self.output_path + "/" + CSV_FILENAME)
        return df
    
    def extract_solution(self, to_csv : bool=True) -> pd.DataFrame:
        """
        Extract data from tbldictionnaire table and from tblsolution as well (jaugecoutsolution, jaugegainsolution)
        
        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        df_sol_dict = self.extract_dictionnaire()

        # Select all rows from tblsolution
        self.cursor.execute("SELECT numsolution, jaugecoutsolution, jaugegainsolution FROM tblsolution")
        data = self.cursor.fetchall()
        df_sol = pd.DataFrame(data, columns=["numsolution", "jauge_cout", "jauge_gain"])
        # Set the index to "numsolution"
        df_sol.set_index("numsolution", inplace=True)
        # Set the index to "numsolution" in df_sol_dict
        df_sol_dict.reset_index(inplace=True)
        df_sol_dict.set_index("numsolution", inplace=True)
        # Merge the two dataframes
        df = pd.merge(df_sol, df_sol_dict, on="numsolution", how="right")

        # Set the index to "numsolution" and "codelangue" and transform the column "codelangue" to int
        df.set_index("codelangue", append=True, inplace=True)

        # Save the result to a CSV file
        if to_csv:
            df.to_csv(self.output_path + "/solution.csv")
        
        return df

    def extract_techno_solution(self) -> pd.DataFrame:
        """
        Extract data from tblsolution and tbltechno tables and save it to a CSV file
        in order to have a list of numsolution and child codetechno for each codetechno
        
        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        CSV_FILENAME = "techno_solution.csv"

        # Select all rows from tblsolution
        self.cursor.execute("SELECT numsolution, codetechno FROM tblsolution")
        solution_techno = self.cursor.fetchall()
        df_sol = pd.DataFrame(solution_techno, columns=["numsolution", "codetechno"])

        # Group by codetechno and create a list of numsolution for each codetechno
        df_sol = df_sol.groupby("codetechno")["numsolution"].apply(list).reset_index()

        # Select all rows from tbltechno
        self.cursor.execute("SELECT numtechno, codeparenttechno FROM tbltechno")
        techno_parent = self.cursor.fetchall()
        df_tech = pd.DataFrame(techno_parent, columns=["codetechno", "codeparenttechno"])

        # Transform the df in order to have one row per codetechno and a list of child codetechno
        df_tech = df_tech.groupby("codeparenttechno")["codetechno"].apply(list).reset_index()
        # Rename the columns
        df_tech.columns = ["codetechno", "sous_techno"]
        # Concatenate the two dataframes
        df = pd.merge(df_tech, df_sol, on="codetechno", how="outer")
        # Rename the first column to "numtechno" and set it as the index
        df.columns = ["numtechno", "sous_techno", "solutions"]
        df.set_index("numtechno", inplace=True)
        # Save the result to a CSV file
        df.to_csv(self.output_path + "/" + CSV_FILENAME)

        return df

    def extract_sectors(self) -> pd.DataFrame:
        """
        Get the sectors association between the sector code and the sector name by extracting the data from tblsecteur
        and using tbldictionnaire to get all information about the sector ("chiffre clés", "définition",...)

        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        CSV_FILENAME = "secteur.csv"
            
        # Select all rows from tblsecteur
        self.cursor.execute("SELECT numsecteur, codeparentsecteur FROM tblsecteur")
        data = self.cursor.fetchall()
        df_sec = pd.DataFrame(data, columns=["numsecteur", "codeparentsecteur"])

        # Extract the data from tbldictionnaire
        df_dict = self.extract_dictionnaire("sec", "secteur", to_csv=False)
        # Keep only the columns "titre", "definition"
        df_dict = df_dict[["titre", "definition"]]
        # Remove the index
        df_dict.reset_index(inplace=True)
        # Merge the two dataframes
        df = pd.merge(df_sec, df_dict, on="numsecteur", how="left")
        # Remove the first line
        df.drop(index=0, inplace=True)
        # Transform the column "codelangue" to int
        df["codelangue"] = df["codelangue"].astype(int)
        # Set the index to "numsecteur"
        df.set_index("numsecteur", inplace=True)
        # Save the result to a CSV file
        df.to_csv(self.output_path + "/" + CSV_FILENAME)

        return df

    def get_rex_sectors(self) -> pd.DataFrame:
        """
        Get data from tblrex in order to link use cases (=rex in french) to sectors
        in order to link later solutions to rex and sectors
        """

        # Select all rows from tblrex
        self.cursor.execute("SELECT numrex, codereference FROM tblrex")
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["numrex", "codereference"])

        # Select all rows from tblreference
        self.cursor.execute("SELECT numreference, codesecteur FROM tblreference")
        data = self.cursor.fetchall()
        df_ref = pd.DataFrame(data, columns=["codereference", "codesecteur"])

        # Merge the two dataframes
        df = pd.merge(df, df_ref, on="codereference", how="left")
        # Set the index to "numrex"
        df.set_index("numrex", inplace=True)
        # Drop the column "codereference"
        df.drop(columns="codereference", inplace=True)

        return df

    def get_code(self, value : int, type_code : str="uni", codelangue : int=2) -> str :
        """
        Get the unit, period or monnaie of an int (founded in tbldictionnairecategories)

        Parameters:
        -----------
            value (int): The value corresponding to the unit or the period
            is_unit (bool): If True, we want an unit, else we want a period
            codelangue (int): The language code

        Returns:
        -------
            str: The unit or the period
        
        Raises:
        -------
            ValueError: If the type_code is not "uni", "per" or "mon" or if the value is 0
        """

        if type_code not in ["uni", "per", "mon"]:
            raise ValueError("type_code must be 'uni', 'per' or 'mon', for 'unité', 'periode' or 'monnaie' respectively")
        if value == 0:
            raise ValueError("0 corresponds to None, so it can't be found in the database")
        
        if type_code == "uni" or type_code == "per":
            # Select the row where the value is equal to the parameter value
            self.cursor.execute("SELECT traductiondictionnairecategories FROM tbldictionnairecategories WHERE typedictionnairecategories = %s AND codelangue = %s AND codeappelobjet = %s", (type_code, str(codelangue), str(value)))
            data = self.cursor.fetchall()
        else :
            # Select the row in tblmonnaie where the value is equal to the parameter value
            self.cursor.execute("SELECT monnaie FROM tblmonnaie WHERE codemonnaie = %s", (value,))
            data = self.cursor.fetchall()
        if not len(data):
                return ""
        return data[0][0]


    def extract_solution_rex(self, to_csv : bool=True) -> pd.DataFrame:
        """
        Get data from tblrex in order to link use cases (=rex in french) to solutions
        For this we need to extract the gainrex and coutrex informations and gather them in a DataFrame

        Parameters:
        -----------
            to_csv (bool): If True, save the result to a CSV file

        Returns:
        -------
            pd.DataFrame: A DataFrame with all needed data for each couple (numsolution, numrex)
        """

        CSV_FILENAME = "solution_rex.csv"

        # Select all rows from coutrex
        self.cursor.execute("SELECT * FROM tblcoutrex")
        data = self.cursor.fetchall()
        df_cout = pd.DataFrame(data, columns=["numcout", "numsolution", "numrex", "mini_cout", "maxi_cout", "reel_cout", "code_monnaie_cout", "code_unite_cout", "difficulte", "license"])
        # Remove the first row, and the last column
        df_cout.drop(index=0, inplace=True) ; df_cout.drop(columns="license", inplace=True)
        # Set the index to "numsolution" and "numrex"
        df_cout.set_index(["numsolution", "numrex"], inplace=True)
        
        # Remove the lines where "minicout", "maxicout", "reelcout" are NaN in the 3 columns
        df_cout = df_cout.dropna(subset=["mini_cout", "maxi_cout", "reel_cout"], how="all")
        # Merge the duplicated indeces into one row by summing the values of the columns if "codemonnaiecout" and "codeunitecout" are the same
        df_cout = df_cout.groupby(level=[0,1]).agg({"mini_cout": "sum", "maxi_cout": "sum", "reel_cout": "sum", 
                                                    "code_monnaie_cout": "first", "code_unite_cout": "first", "difficulte": "mean"})
        
        # Select all rows from gainrex
        self.cursor.execute("SELECT * FROM tblgainrex")
        data = self.cursor.fetchall()
        df_gain = pd.DataFrame(data, columns=["numgain", "numsolution", "numrex", "gain", 
                                              "code_monnaie_gain", "code_periode_gain", "energie_gain", 
                                              "code_unite_energie", "code_periode_energie", "ges_gain", 
                                              "mini_gain", "maxi_gain", "moyen_gain", "reel_gain", "tri_reel", 
                                              "tri_min", "tri_max", "license"])
        # Remove the first row, and the last column
        df_gain.drop(index=0, inplace=True) ; df_gain.drop(columns="license", inplace=True)
        # Set the index to "numsolution" and "numrex"
        df_gain.set_index(["numsolution", "numrex"], inplace=True)
        # Drop the column "numgain"
        df_gain.drop(columns="numgain", inplace=True)

        # Remove the lines where "gain", "energiegain", "gesgain", "minigain", "maxigain", "moyengain", "reelgain", "trireel", "trimin", "trimax" are NaN in the 10 columns
        df_gain = df_gain.dropna(subset=["gain", "energie_gain", "ges_gain", "mini_gain", "maxi_gain", "moyen_gain", "reel_gain", "tri_reel", "tri_min", "tri_max"], how="all")
        
        # Merge df_cout and df_gain on the index
        df = pd.merge(df_cout, df_gain, on=["numsolution", "numrex"], how="outer")

        # Transform the columns that start with "code" to int (if they are not NaN)
        columns = [col for col in df.columns if col.startswith("code")]
        for col in columns:
            df[col] = df[col].apply(lambda x: 0 if pd.isnull(x) else x)
            df[col] = df[col].astype(int)
        
        df["difficulte"] = df["difficulte"].apply(lambda x: int(x) if not pd.isnull(x) else x)

        if to_csv:
            df.to_csv(self.output_path + "/" + CSV_FILENAME)

        return df


    def extract_sector_solution(self, df_sol_rex : pd.DataFrame, to_csv : bool=True) -> pd.DataFrame:
        """
        Get data from tblsecteur in order to link sectors to solutions
        We will use the df_sol_rex DataFrame that links solutions to rex and "get_rex_sectors" to link rex to sectors

        Parameters:
        -----------
            df_sol_rex (pd.DataFrame): The DataFrame that links solutions to rex
            to_csv (bool): If True, save the result to a CSV file
        
        Returns:
        -------
            pd.DataFrame: A DataFrame that has "numsecteur" as index and "sous_secteurs", "solutions" as columns
        """

        # Get the association between rex and sectors
        df_rex_sec = self.get_rex_sectors()
        # Remove the first row
        df_rex_sec.drop(index=1, inplace=True)

        # Get the list of solutions for each rex
        df_sol_rex = df_sol_rex.reset_index()
        df_sol_rex = df_sol_rex.groupby("numrex")["numsolution"].apply(list).reset_index()
        df_sol_rex.set_index("numrex", inplace=True)
        # Remove all other columns than "numsolution"
        df_sol_rex = df_sol_rex[["numsolution"]]
        
        # Merge the two dataframes (inner because there are rex without solutions and vice versa)
        df_sec_sol = pd.merge(df_rex_sec, df_sol_rex, on="numrex", how="inner")
        # Reset the index and remove "numrex" and rename the column "codesecteur" into "numsecteur" and "solutions" into "solutions"
        df_sec_sol.reset_index(inplace=True) ; df_sec_sol.drop(columns="numrex", inplace=True)
        df_sec_sol.rename(columns={"codesecteur": "numsecteur", "numsolution": "solutions"}, inplace=True)
        # Group by "numsecteur" and aggregate the values of "solutions" into a list (flatten the list)
        df_sec_sol = df_sec_sol.groupby("numsecteur")["solutions"].apply(lambda x: [item for sublist in x for item in sublist]).reset_index()
        # Remove duplicated solutions in the lists
        df_sec_sol["solutions"] = df_sec_sol["solutions"].apply(lambda x: list(set(x)))
        # Set the index to "numsecteur"
        df_sec_sol.set_index("numsecteur", inplace=True)


        # Select all rows from tblsecteur (to get the parent sector of each sector)
        self.cursor.execute("SELECT numsecteur, codeparentsecteur FROM tblsecteur")

        data = self.cursor.fetchall()
        df_sec = pd.DataFrame(data, columns=["numsecteur", "codeparentsecteur"])

        # Get the association between a sector and its child sectors
        df_sec = df_sec.groupby("codeparentsecteur")["numsecteur"].apply(list).reset_index()
        df_sec.columns = ["numsecteur", "sous_secteurs"]

        # Merge the two dataframes
        df_sec_sol = pd.merge(df_sec, df_sec_sol, on="numsecteur", how="outer")
        # Set the index to "numsecteur"
        df_sec_sol.set_index("numsecteur", inplace=True)

        if to_csv:
            df_sec_sol.to_csv(self.output_path + "/secteur_solution.csv")

        return df_sec_sol

    def extract_monnaie(self, to_csv : bool=True) -> pd.DataFrame:
        """
        Get data from tblmonnaie in order to have a list of monnaie and their associated code

        Parameters:
        -----------
            to_csv (bool): If True, save the result to a CSV file

        Returns:
        -------
            pd.DataFrame: A DataFrame with the extracted data
        """

        CSV_FILENAME = "monnaie.csv"

        # Select all rows from tblmonnaie
        self.cursor.execute("SELECT * FROM tblmonnaie")
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["codemonnaie", "monnaie"])

        # Get rates of the currencies in euros using the API https://api.exchangerate-api.com/v4/latest/EUR
        response = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
        rates = response.json()["rates"]

        # Add a column "rate" to get the rate of the currency in euros
        df["rate"] = df["monnaie"].apply(lambda x: rates.get(x, None))

        # For "FRF" (French Franc)
        df.loc[df["monnaie"] == "FRF", "rate"] = 6.55957
        # For "LACS"
        df.loc[df["monnaie"] == "LACS", "rate"] = 14029.14

        # Set the index to "codemonnaie"
        df.set_index("codemonnaie", inplace=True)

        # Remove the first row
        df.drop(index=1, inplace=True)

        if to_csv:
            df.to_csv(self.output_path + "/" + CSV_FILENAME)

        return df

if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_solution()
    extractor.extract_dictionnaire("tec", "technologie") # Technologies
    extractor.extract_techno_solution()
    extractor.extract_sectors()
    df_sol_rex = extractor.extract_solution_rex()
    extractor.extract_sector_solution(df_sol_rex)
    df_unit = extractor.extract_dictionnaire_categories("uni", "unite") # Units
    extractor.extract_dictionnaire_categories("per", "periode") # Periods
    extractor.extract_monnaie() # Currencies

