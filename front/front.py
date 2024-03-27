import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils import get_sectors, find_best_solutions, get_solutions_info_by_id, bag_of_words

import uvicorn

app = FastAPI()

# Montage des fichiers statiques (CSS, JavaScript, etc.)
app.mount("/static", StaticFiles(directory="front/static"), name="static")

# Utilisation de templates Jinja2 pour la gestion des pages HTML
templates = Jinja2Templates(directory="front/templates")

# Obtenir les noms à partir de get_name
dropdown_options = get_sectors()
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
        if option['name'] == selected_option:
            sector_number = option["code"]
            break
        for _, sub_option in enumerate(option.get('sub_secteurs', [])):
            if sub_option['name'] == selected_option:
                sector_number = option["code"]
                sub_sector_number = sub_option["code"]
                break
   

    # Find the best solutions
    best_solutions = find_best_solutions(user_input, sub_sector_number, sector_number, 20)

    best_solutions = get_solutions_info_by_id(best_solutions)

    # Return the best solutions in the message
    return {"solutions": best_solutions}

# Function to run a Bag of Words model on the user input to detect technologies in it
@app.post("/bow/")
async def bow(dict_data: dict):

    user_input = dict_data.get('user_input')

    # Run the Bag of Words model
    technos = bag_of_words(user_input)

    # Return the technologies found
    return {"data": technos}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
