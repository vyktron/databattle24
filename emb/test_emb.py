from emb import embeddings, cosine_similarity, important_words

data_set = ""
lang = "french"
model_name = "google-bert/bert-base-multilingual-cased"
sentences = ["Comment faire pour réduire la consommation de mon compresseur d'air comprimé ?", 
             "J'aimerais avoir une régulation optimisée de mon groupe froid",
             "Comment optimiser la production de mon compresseur à air comprimé ?",
             "Comment utiliser un compresseur avec mon chien ?"]

#make embeddings
emb = []
for s in sentences:
    emb.append(embeddings(model_name, s, lang))

for i in range(len(emb)-1):
    print(sentences[i] + " - " + sentences[i+1] + "  simi : ", cosine_similarity(emb[i], emb[i+1]))

print(sentences[0] + " - " + sentences[2] + "  simi : ", cosine_similarity(emb[0], emb[2]))


#make most importante word
for s in sentences:
    words = important_words(model_name, s, lang)
    print(s, words)