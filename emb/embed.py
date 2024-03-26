import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from nltk.corpus import stopwords
import pandas as pd
import numpy as np

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#import nltk
#nltk.download('stopwords')

TOKENIZERS_PARALLELISM = True

#embeddings
def embeddings(sentence, model_name, lang):

    stopword = set(stopwords.words(lang))

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)

    tokens = tokenizer.tokenize(sentence, max_length=None, truncation=True)
    filtered_tokens = [x for x in tokens if x not in stopword]

    input_ids = tokenizer.convert_tokens_to_ids(filtered_tokens)

    with torch.no_grad():
        outputs = model(torch.tensor([input_ids]))

    emb = outputs.last_hidden_state[:, 0, :]

    return emb


# Compute cosine similarity
def cosine_similarity(emb1, emb2):
    
    # Normalize embeddings
    emb1_norm = F.normalize(emb1, p=2, dim=1)
    emb2_norm = F.normalize(emb2, p=2, dim=1)
    
    # Compute cosine similarity
    similarity = torch.cosine_similarity(emb1_norm, emb2_norm, dim=1)
    return similarity.item()



#return id row of dataframe, the most closest answer
def find_answer_to_query(query, list_emb, nb_ans, model_name, lang):

    query_emb = embeddings(query, model_name, lang)

    cos_sim = []
    for emb in list_emb:
        cos_sim.append(cosine_similarity(emb, query_emb))

    id_max_list = []
    for i in range(nb_ans):
        id_max = cos_sim.index(max(cos_sim))
        id_max_list.append(id_max)
        cos_sim[id_max] = 0
    
    return id_max_list


#return most important word in the senteces
def important_words(sentence, model_name, lang):

    stopword = set(stopwords.words(lang))

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)

    tokens = tokenizer.tokenize(sentence)
    filtered_tokens = [x for x in tokens if x not in stopword]
    input_ids = tokenizer.convert_tokens_to_ids(filtered_tokens)

    with torch.no_grad():
        outputs = model(torch.tensor([input_ids]))

    attention_weights = outputs.attentions[-1]
    weighted_embeddings = torch.matmul(attention_weights, outputs.last_hidden_state)
    importance_scores = torch.norm(weighted_embeddings, dim=-1)

    top_indices = importance_scores.argsort(descending=True).tolist()[0][0]
    tokens = tokenizer.convert_ids_to_tokens(input_ids)
    important_words = [tokens[i] for i in top_indices]

    return important_words


def stock_embeddings(list_emb):

    list_emb = np.concatenate([emb.numpy().reshape(1, -1) for emb in list_emb])

    df = pd.DataFrame(list_emb)
    csv_file_path = "embeddings.csv"
    df.to_csv(csv_file_path, index=False)

    print("embeddings stock in embeddings.csv")


def load_embeddings(csv_path):

    df = pd.read_csv(csv_path)
    list_emb = df.values.tolist()

    return list_emb