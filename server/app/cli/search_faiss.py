import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Laden des Modells
model = SentenceTransformer('all-MiniLM-L6-v2')

# Laden des Faiss Index
index = faiss.read_index("dokumente_index.faiss")

# Laden der ursprünglichen Dokumente oder Metadaten
# (Annahme: wir haben eine Liste von Dokumententiteln oder Inhalten)
with open("metadata.pkl", "rb") as f:
    dokumente = pickle.load(f)

def suche(query_text, k=5):
    # Umwandlung des Suchtexts in ein Embedding
    query_embedding = model.encode([query_text])[0]

    # Suche nach den k ähnlichsten Dokumenten
    D, I = index.search(query_embedding.reshape(1, -1), k)

    print(f"Suchanfrage: '{query_text}'")
    print("\nErgebnisse:")
    for i, (idx, dist) in enumerate(zip(I[0], D[0])):
        print(f"{i+1}. Dokument: {dokumente[idx]}")
        print(f"   Ähnlichkeit: {1 - dist:.4f}")  # Umwandlung der Distanz in Ähnlichkeit
        print()

# Beispiel-Suchanfragen
suche("Künstliche Intelligenz in der Medizin")
