import math
from collections import Counter
import string

def tokenize(text):
    """Convert text to lowercase and split into words"""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

def preprocess(text):
    """Remove stop words and non-alphabetic tokens"""
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'is', 'are', 'of', 'in', 'on', 'to',
        'for', 'with', 'as', 'by', 'at', 'be', 'that', 'this', 'it', 'has',
        'have', 'but', 'not'
    }
    tokens = tokenize(text)
    return [word for word in tokens if word not in stop_words and word.isalpha()]

def compute_tf(tokens):
    """Calculate term frequency for each word in the document"""
    total_words = len(tokens)
    return {word: count / total_words for word, count in Counter(tokens).items()}

def compute_idf(corpus):
    """Calculate inverse document frequency for each term in the corpus"""
    df = {}
    for doc in corpus:
        unique_terms = set(doc)
        for term in unique_terms:
            df[term] = df.get(term, 0) + 1
    n_docs = len(corpus)
    return {term: math.log(n_docs / count) for term, count in df.items()}

def compute_tfidf(tf, idf):
    """Calculate TF-IDF weights for a document"""
    return {term: tf[term] * idf[term] for term in tf if term in idf}

def query_tfidf(query, idf):
    """Calculate TF-IDF weights for a query using corpus IDF values"""
    tokens = preprocess(query)
    tf = compute_tf(tokens)
    return {term: tf[term] * idf[term] for term in tf if term in idf}

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two TF-IDF vectors"""
    
    # Calculate magnitudes
    mag1 = math.sqrt(sum(val**2 for val in vec1.values()))
    mag2 = math.sqrt(sum(val**2 for val in vec2.values()))
    
    # Handle zero vectors
    if mag1 == 0 or mag2 == 0:
        return 0.0

    # Get all unique terms from both vectors
    terms = set(vec1) | set(vec2)

    # Calculate dot product
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in terms)
    
    
    return dot_product / (mag1 * mag2)

def main():
    # Sample corpus
    corpus_texts = [
        "Machine learning is the study of computer algorithms that improve automatically through experience.",
        "Deep learning is a subset of machine learning involving neural networks with many layers.",
        "Natural language processing is a field of artificial intelligence that focuses on the interaction between computers and humans."
    ]
    
    # Preprocess corpus
    corpus = [preprocess(text) for text in corpus_texts]
    
    # Compute IDF values
    idf = compute_idf(corpus)
    
    # Compute TF-IDF vectors for each document
    doc_tfidf = [compute_tfidf(compute_tf(doc), idf) for doc in corpus]
    
    def retrieve_context(query, top_n=2):
        """Retrieve most relevant documents for a given query"""
        query_vec = query_tfidf(query, idf)
        
        if not query_vec:
            return ["No relevant documents found."]
        
        # Calculate similarity with each document
        similarities = [
            cosine_similarity(query_vec, doc_vec) 
            for doc_vec in doc_tfidf
        ]
        
        # Rank documents by similarity
        ranked_indices = [
            i for i, _ in sorted(
                enumerate(similarities), 
                key=lambda x: x[1], 
                reverse=True
            )
        ]
        
        # Return top N results
        return [corpus_texts[i] for i in ranked_indices[:top_n]]
    
    # Example usage
    query = "What is deep learning?"
    results = retrieve_context(query)
    
    print(f"Query: {query}\n")
    for i, doc in enumerate(results, 1):
        print(f"Top {i}: {doc}")

if __name__ == "__main__":
    main()