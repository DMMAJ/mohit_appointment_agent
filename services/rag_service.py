from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from typing import List
import json
import os

class RAGService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = "clinic_faq"
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384
    
    def setup_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection '{self.collection_name}'")
    
    def ingest_faqs(self):
        """Load and ingest FAQ data into Qdrant"""
        with open("data/clinic_info.json", 'r') as f:
            faqs = json.load(f)
        
        points = []
        for faq in faqs:
            # Combine question and answer for better retrieval
            text = f"{faq['question']} {faq['answer']}"
            vector = self.encoder.encode(text).tolist()
            
            points.append(PointStruct(
                id=int(faq['id']),
                vector=vector,
                payload={
                    "question": faq['question'],
                    "answer": faq['answer']
                }
            ))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Ingested {len(points)} FAQs into Qdrant")
    
    def search_faq(self, query: str, limit: int = 2) -> List[dict]:
        """Search for relevant FAQs"""
        query_vector = self.encoder.encode(query).tolist()
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [
            {
                "question": hit.payload["question"],
                "answer": hit.payload["answer"],
                "score": hit.score
            }
            for hit in results
        ]

rag_service = RAGService()