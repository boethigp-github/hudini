import pickle
import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

# Load the original texts (you'll need to have saved these alongside the embeddings)
with open('embeddings_output.pkl', 'rb') as f:
    texts = pickle.load(f)

# Create a CountVectorizer
vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
doc_term_matrix = vectorizer.fit_transform(texts)

# Create and fit the LDA model
lda_model = LatentDirichletAllocation(n_components=5, random_state=42)
lda_output = lda_model.fit_transform(doc_term_matrix)

# Function to print top words for each topic
def print_topics(model, feature_names, top_n=10):
    for idx, topic in enumerate(model.components_):
        print(f"Topic {idx + 1}:")
        print(", ".join([feature_names[i] for i in topic.argsort()[:-top_n - 1:-1]]))
        print()

# Print the topics
print_topics(lda_model, vectorizer.get_feature_names_out())

# Print the dominant topic for each document
for i, doc_topics in enumerate(lda_output):
    dominant_topic = doc_topics.argmax()
    print(f"Document {i}: Dominant Topic {dominant_topic + 1}")