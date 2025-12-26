"""
Domain classification and query routing for the Council Query Assistant.
"""

from typing import Dict, List, Optional
import re
import numpy as np
from embedding import EmbeddingModel


class DomainClassifier:
    """
    Classifies documents and queries into predefined domains for better retrieval.
    """

    # Domain mapping based on document filenames
    DOMAIN_MAPPING = {
        "bylaws": "by-laws",
        "operating_licenses": "licensing",
        "bill_payments": "billing",
        "public_notices": "notices",
        "council_contacts": "contacts",
        "departments": "departments",
        "faq": "faq",
        "glossary": "glossary",
        "online_services": "services",
        "water_distribution": "utilities",
        "about_me": "general"
    }

    # Keywords for domain classification
    DOMAIN_KEYWORDS = {
        "by-laws": ["bylaw", "law", "regulation", "rule", "ordinance", "code", "statute"],
        "licensing": ["license", "permit", "certification", "approval", "registration"],
        "billing": ["bill", "payment", "fee", "charge", "invoice", "rate", "cost"],
        "notices": ["notice", "announcement", "public notice", "advisory", "alert"],
        "contacts": ["contact", "phone", "email", "address", "department", "office"],
        "departments": ["department", "division", "section", "unit", "branch"],
        "faq": ["faq", "question", "answer", "frequently", "asked"],
        "glossary": ["glossary", "term", "definition", "meaning"],
        "services": ["service", "online", "portal", "application", "form"],
        "utilities": ["water", "electricity", "utility", "infrastructure", "distribution"],
        "general": ["about", "overview", "introduction", "general", "information"]
    }

    def __init__(self, use_embeddings: bool = False):
        """
        Initialize the domain classifier.

        Args:
            use_embeddings: Whether to use embeddings for classification (more accurate but slower)
        """
        self.use_embeddings = use_embeddings
        if use_embeddings:
            self.embedding_model = EmbeddingModel()
            # Pre-compute domain embeddings
            self.domain_embeddings = {}
            for domain, keywords in self.DOMAIN_KEYWORDS.items():
                # Create a representative text for each domain
                domain_text = " ".join(keywords)
                self.domain_embeddings[domain] = self.embedding_model.embed([domain_text])[0]

    def classify_document(self, filename: str) -> str:
        """
        Classify a document into a domain based on its filename.

        Args:
            filename: The filename of the document

        Returns:
            Domain label
        """
        # Remove extension and convert to lowercase
        base_name = filename.lower().replace('.txt', '').replace('.json', '')

        # Direct mapping first
        if base_name in self.DOMAIN_MAPPING:
            return self.DOMAIN_MAPPING[base_name]

        # Keyword matching as fallback
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in base_name for keyword in keywords):
                return domain

        # Default to general
        return "general"

    def classify_query(self, query: str) -> str:
        """
        Classify a user query into a domain.

        Args:
            query: The user's query

        Returns:
            Domain label
        """
        query_lower = query.lower()

        if self.use_embeddings:
            return self._classify_with_embeddings(query)
        else:
            return self._classify_with_keywords(query_lower)

    def _classify_with_keywords(self, query_lower: str) -> str:
        """
        Classify query using keyword matching.
        """
        # Count keyword matches for each domain
        domain_scores = {}

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            # Return domain with highest score
            return max(domain_scores, key=domain_scores.get)

        return "general"

    def _classify_with_embeddings(self, query: str) -> str:
        """
        Classify query using embeddings (semantic similarity).
        """
        query_embedding = self.embedding_model.embed([query])[0]

        best_domain = "general"
        best_similarity = -1

        for domain, domain_embedding in self.domain_embeddings.items():
            # Simple cosine similarity
            similarity = self._cosine_similarity(query_embedding, domain_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_domain = domain

        return best_domain

    def _cosine_similarity(self, vec1, vec2) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_available_domains(self) -> List[str]:
        """
        Get list of all available domains.
        """
        return list(self.DOMAIN_KEYWORDS.keys())