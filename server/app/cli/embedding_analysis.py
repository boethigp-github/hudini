import pickle
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load the embeddings
with open('embeddings_output.pkl', 'rb') as f:
    embeddings = pickle.load(f)

# Print information about the embeddings
print(f"Type of embeddings: {type(embeddings)}")
print(f"Shape of embeddings: {np.array(embeddings).shape}")

# Convert embeddings to numpy array if it's not already
embeddings_array = np.array(embeddings)

# Perform K-means clustering
n_clusters = 5  # You can adjust this number
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(embeddings_array)


# Function to find most representative documents for each cluster
def get_representative_docs(embeddings, labels, n_docs=3):
    centroids = kmeans.cluster_centers_
    representatives = []
    for i in range(n_clusters):
        cluster_docs = embeddings[labels == i]
        similarities = cosine_similarity(cluster_docs, [centroids[i]])
        top_indices = similarities.argsort(axis=0)[-n_docs:][::-1].flatten()
        cluster_indices = np.where(labels == i)[0]
        representatives.append(cluster_indices[top_indices])
    return representatives


# Get representative documents
representative_docs = get_representative_docs(embeddings_array, cluster_labels)

# Load the model (make sure it's the same one used for generating embeddings)
model = SentenceTransformer('all-MiniLM-L6-v2')


# Function to get words from embeddings
def get_words_from_embedding(embedding, top_n=10):
    # Create a large vocabulary
    vocabulary = model.tokenizer.get_vocab()
    words = list(vocabulary.keys())
    word_embeddings = model.encode(words)

    # Calculate cosine similarity
    similarities = cosine_similarity([embedding], word_embeddings)[0]

    # Get top N words
    top_indices = similarities.argsort()[-top_n:][::-1]
    return [words[i] for i in top_indices]


# Print results
for i, cluster_reps in enumerate(representative_docs):
    print(f"Cluster {i + 1}:")
    print(f"Representative document indices: {cluster_reps}")

    # Get words for the centroid of this cluster
    centroid_words = get_words_from_embedding(kmeans.cluster_centers_[i])
    print(f"Top words for this cluster: {', '.join(centroid_words)}")
    print()

# Print cluster for each document
for i, label in enumerate(cluster_labels):
    print(f"Document {i}: Cluster {label + 1}")