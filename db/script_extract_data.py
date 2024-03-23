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

        CSV_FILENAME = "dictionary.csv"

        self.cursor.execute("SELECT * FROM tbldictionnaire WHERE typedictionnaire = 'sol' OR typedictionnaire = 'tec'")
        data = self.cursor.fetchall()
        df = pd.DataFrame(data, columns=["id", "codelangue", "typedictionnaire", "codeappelobjet", "indexdictionnaire", "texte"])
        df["texte"] = df["texte"].apply(lambda x: re.sub(r"<[^>]*>", "", x))
        df["texte"] = df["texte"].apply(lambda x: unescape(x))
        merged_df = df.pivot_table(index=["typedictionnaire", "codeappelobjet", "codelangue"], columns="indexdictionnaire", values="texte", aggfunc=lambda x: ' '.join(x))
        merged_df.to_csv(self.output_path + "/" + CSV_FILENAME)

    def extract_tblsolution(self):

        CSV_FILENAME = "techno_solution.csv"

        self.cursor.execute("SELECT numsolution, codetechno FROM tblsolution")
        solution_techno = self.cursor.fetchall()
        df = pd.DataFrame(solution_techno, columns=["numsolution", "codetechno"])
        df = df.groupby("codetechno")["numsolution"].apply(list).reset_index()
        df.to_csv(self.output_path + "/" + CSV_FILENAME, index=False)


if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_tbldictionnaire()
    extractor.extract_tblsolution()
