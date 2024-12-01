import faiss
import numpy as np
import pickle

# Laden der Embeddings
with open('embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)

# Konvertieren zu numpy array falls nötig
embeddings_array = np.array(embeddings).astype('float32')

# Dimensionalität der Embeddings
d = embeddings_array.shape[1]

# Erstellen des Index
index = faiss.IndexFlatL2(d)

# Hinzufügen der Embeddings zum Index
index.add(embeddings_array)

# Speichern des Index
faiss.write_index(index, "dokumente_index.faiss")

print(f"Index erstellt und gespeichert. Enthält {index.ntotal} Vektoren.")