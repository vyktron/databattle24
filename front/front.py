import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import get_name

import uvicorn

app = FastAPI()

# Montage des fichiers statiques (CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Utilisation de templates Jinja2 pour la gestion des pages HTML
templates = Jinja2Templates(directory="templates")

# Obtenir les noms à partir de get_name
names_data = get_name()

# Création d'une liste pour stocker les options
dropdown_options = []

# Boucle sur les données pour obtenir les noms principaux et leurs sous-options
for data in names_data:
    option = {'name': data['name']}  # Ajout du nom principal
    if data.get('sub_secteurs'):  # Vérification s'il y a des sous-options
        sub_options = [{'name': f"-- {sub_data['name']}", 'value': sub_data['name']} for sub_data in data['sub_secteurs']]
        option['sub_options'] = sub_options
    dropdown_options.append(option)

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "dropdown_options": dropdown_options})

# Fonction pour traiter les données envoyées par le formulaire
@app.post("/submit/")
async def submit_data(request: Request, selected_option: str, user_input: str):
    # Utilisez ici les données pour effectuer le traitement nécessaire
    print("Option sélectionnée:", selected_option)
    print("Texte de l'utilisateur:", user_input)
    return {"message": "Données reçues avec succès"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
