# tools/rag_engine.py
"""
RAG (Retrieval Augmented Generation) Engine for Q&A over PDF documents
"""
import os
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Tuple

class RAGEngine:
    """Handles document chunking, retrieval, and context building for Q&A"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Initialize RAG engine
        
        Args:
            chunk_size: Number of characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
    
    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract full text from PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text from PDF
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF: {str(e)}")
            return ""
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Full text to chunk
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
        
        return chunks
    
    def build_index(self, pdf_path: str):
        """
        Build searchable index from PDF
        
        Args:
            pdf_path: Path to PDF file
        """
        # Extract text
        text = self.extract_pdf_text(pdf_path)
        
        if not text:
            raise ValueError("Could not extract text from PDF")
        
        # Chunk text
        self.chunks = self.chunk_text(text)
        
        if not self.chunks:
            raise ValueError("No valid chunks created from PDF")
        
        # Build TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
        except Exception as e:
            print(f"Error building index: {str(e)}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            query: Search query
            top_k: Number of top results to return
        
        Returns:
            List of (chunk_text, similarity_score) tuples
        """
        if self.vectorizer is None or self.tfidf_matrix is None:
            return []
        
        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Return chunks with scores
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include relevant results
                    results.append((self.chunks[idx], float(similarities[idx])))
            
            return results
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}")
            return []
    
    def build_context(self, query: str, top_k: int = 5) -> str:
        """
        Build context string from relevant chunks
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
        
        Returns:
            Context string for LLM
        """
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k)
        
        if not relevant_chunks:
            return ""
        
        context = "Relevant document excerpts:\n\n"
        for i, (chunk, score) in enumerate(relevant_chunks, 1):
            context += f"[Source {i} - Relevance: {score:.2f}]\n{chunk}\n\n"
        
        return context
