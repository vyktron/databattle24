import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import get_name, test

import uvicorn

app = FastAPI()

# Montage des fichiers statiques (CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Utilisation de templates Jinja2 pour la gestion des pages HTML
templates = Jinja2Templates(directory="templates")

# Obtenir les noms à partir de get_name
dropdown_options = get_name()
# Boucle sur les données pour obtenir les noms principaux et leurs sous-options

# Page d'accueil
@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "dropdown_options": dropdown_options})

# Deal with user input (sector, sub_sector and query)
@app.post("/submit/")
async def submit_form(dict_data: dict):

    user_input = dict_data.get('user_input')
    selected_option = dict_data.get('selected_option')

    sector_number = None
    sub_sector_number = None
    # Find the number of the sector assiocated with the selected_option
    for _, option in enumerate(dropdown_options):
        print(option, selected_option)
        if option['name'] == selected_option:
            sector_number = option["code"]
            break
        for _, sub_option in enumerate(option.get('sub_secteurs', [])):
            print(sub_option, selected_option)
            if sub_option['name'] == selected_option:
                sector_number = option["code"]
                sub_sector_number = sub_option["code"]
                break

    message = f"Données reçues avec succès: {user_input} / {selected_option} / {sector_number} / {sub_sector_number}"
    # Renvoyez une réponse avec un message approprié
    return {"message": message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
