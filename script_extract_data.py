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

# Group the "texte" column by "codeappelobjet" and "indexdictionnaire"
df = df.groupby(["codelangue", "codeappelobjet"])["texte"].apply(lambda x: " ".join(x)).reset_index()

# Remove html balises in the "texte" column
import re
df["texte"] = df["texte"].apply(lambda x: re.sub(r"<[^>]*>", "", x))

# Handle french accents to transform "&ecirc;" in "ê" for example
from html import unescape
df["texte"] = df["texte"].apply(lambda x: unescape(x))

# Save the dataframe to a CSV file
df.to_csv("data.csv", index=False)
