import mysql.connector

# Connect to the MySQL server
cnx = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="user",
    password="password",
    database="kerdos"
)

# Create a new database if it doesn't exist
cursor = cnx.cursor()

# Show tables
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# Extract table "tbldictionnaire" where "codeappelobjet" is "sol" or "tec", and "indexdicionnaire" is "1" or "2" or "5"
cursor.execute("SELECT * FROM tbldictionnaire WHERE typedictionnaire = 'sol' OR typedictionnaire = 'tec'")
data = cursor.fetchall()


# Put all in a dataframe
import pandas as pd

df = pd.DataFrame(data, columns=["id", "codelangue", "typedictionnaire", "codeappelobjet", "indexdictionnaire", "texte"])

# Remove html balises in the "texte" column
import re
df["texte"] = df["texte"].apply(lambda x: re.sub(r"<[^>]*>", "", x))

# Handle french accents to transform "&ecirc;" in "ê" for example
from html import unescape
df["texte"] = df["texte"].apply(lambda x: unescape(x))

merged_df = df.pivot_table(index=["codelangue", "typedictionnaire", "codeappelobjet"], columns="indexdictionnaire", values="texte", aggfunc=lambda x: ' '.join(x))

# Save the dataframe to a CSV file
merged_df.to_csv("data.csv")

# Get the data from "tblsolution" and extract "numsolution" and "codetechno"
cursor.execute("SELECT numsolution, codetechno FROM tblsolution")
solution_techno = cursor.fetchall()

df = pd.DataFrame(solution_techno, columns=["numsolution", "codetechno"])
# Group by "codetechno" and create a list of "numsolution"
df = df.groupby("codetechno")["numsolution"].apply(list).reset_index()

# Save the dataframe to a CSV file
df.to_csv("solution_techno.csv", index=False)