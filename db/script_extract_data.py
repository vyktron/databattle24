import mysql.connector
import pandas as pd
import re
from html import unescape

class Extractor:
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

    def extract_tbldictionnaire(self):
        """
        Extract data from tbldictionnaire table and save it to a CSV file
        More precisely, we extract the columns "typedictionnaire", "codeappelobjet", "codelangue", "indexdictionnaire", and the associated "texte"
        and save it to a CSV file
        """

        CSV_FILENAME = "dictionnary.csv"

        # Select all rows where typedictionnaire is either "sol" or "tec"
        self.cursor.execute("SELECT * FROM tbldictionnaire WHERE typedictionnaire = 'sol' OR typedictionnaire = 'tec'")
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["id", "codelangue", "typedictionnaire", "codeappelobjet", "indexdictionnaire", "texte"])

        # Remove HTML tags and unescape HTML entities
        df["texte"] = df["texte"].apply(lambda x: re.sub(r"<[^>]*>", "", x))
        df["texte"] = df["texte"].apply(lambda x: unescape(x))

        # Pivot table to have one row per (typedictionnaire, codeappelobjet, codelangue) combination
        merged_df = df.pivot_table(index=["typedictionnaire", "codeappelobjet", "codelangue"], columns="indexdictionnaire", values="texte", aggfunc=lambda x: ' '.join(x))
        merged_df.to_csv(self.output_path + "/" + CSV_FILENAME)

    def extract_tblsolution(self):
        """
        Extract data from tblsolution and tbltechno tables and save it to a CSV file
        in order to have a list of numsolution and child codetechno for each codetechno"""

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
        df_tech.columns = ["codetechno", "child_techno"]
        # Concatenate the two dataframes
        df = pd.merge(df_tech, df_sol, on="codetechno", how="outer")
        # Rename the first column to "numtechno"
        df.columns = ["numtechno", "child_techno", "numsolution"]
        # Save the result to a CSV file
        df.to_csv(self.output_path + "/" + CSV_FILENAME, index=False)


if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_tbldictionnaire()
    extractor.extract_tblsolution()
