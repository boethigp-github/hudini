import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import os

# Laden des Modells
model = SentenceTransformer('all-MiniLM-L6-v2')

# Laden der Embeddings
with open('embeddings_output.pkl', 'rb') as f:
    embeddings = pickle.load(f)

# Konvertieren zu numpy array falls nötig
embeddings_array = np.array(embeddings).astype('float32')

# Erstellen oder Laden des Index
index_file = "dokumente_index.faiss"
if os.path.exists(index_file):
    print("Lade existierenden Index...")
    index = faiss.read_index(index_file)
else:
    print("Erstelle neuen Index...")
    d = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings_array)
    faiss.write_index(index, index_file)

# Laden der Dokument-Metadaten (z.B. Titel oder erste paar Zeilen)
# Ersetzen Sie dies durch Ihre tatsächlichen Metadaten
dokument_metadaten = [f"Dokument {i}" for i in range(len(embeddings))]

def semantic_search(query, top_k=5):
    # Erstellen des Query-Embeddings
    query_embedding = model.encode([query])[0]

    # Suche
    D, I = index.search(query_embedding.reshape(1, -1), top_k)

    print(f"\nSuchergebnisse für: '{query}'")
    print("-" * 50)
    for i, (idx, score) in enumerate(zip(I[0], D[0]), 1):
        print(f"{i}. {dokument_metadaten[idx]}")
        print(f"   Ähnlichkeitswert: {1 - score:.4f}")
        print(f"   Index: {idx}")
        print()

# Beispiel-Suchen
semantic_search("Künstliche Intelligenz")
semantic_search("Klimawandel und Nachhaltigkeit")
semantic_search("Gesundheit und Ernährung")

# Interaktive Suche
while True:
    query = input("\nGeben Sie einen Suchbegriff ein (oder 'q' zum Beenden): ")
    if query.lower() == 'q':
        break
    semantic_search(query)