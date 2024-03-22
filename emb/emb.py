import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from nltk.corpus import stopwords

#import nltk
#nltk.download('stopwords')


#embeddings
def embeddings(sentence, max_length, model_name, lang):

    stopword = set(stopwords.words(lang))

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_attentions=True)

    tokens = tokenizer.tokenize(sentence, max_length=max_length, truncation=True)
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