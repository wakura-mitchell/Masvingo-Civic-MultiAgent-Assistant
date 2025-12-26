"""
Retrieval evaluation system for the Council Query Assistant.
"""

import json
import os
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np
from datetime import datetime
import pandas as pd


class RetrievalEvaluator:
    """
    Evaluates retrieval quality using test queries with expected answers.
    """

    def __init__(self, vector_db, domain_classifier=None):
        """
        Initialize the evaluator.

        Args:
            vector_db: VectorDB instance for retrieval
            domain_classifier: Optional domain classifier
        """
        self.vector_db = vector_db
        self.domain_classifier = domain_classifier
        self.test_queries = []
        self.evaluation_results = []

    def load_test_queries(self, test_file: str = "test_queries.json") -> None:
        """
        Load test queries from a JSON file.

        Expected format:
        [
            {
                "query": "What are the council bylaws?",
                "expected_domains": ["by-laws"],
                "expected_chunks": ["bylaws.txt_0", "bylaws.txt_1"],
                "relevance_threshold": 0.7
            }
        ]
        """
        filepath = os.path.join(os.path.dirname(__file__), "..", test_file)
        if not os.path.exists(filepath):
            print(f"Test file {filepath} not found. Creating sample test queries.")
            self._create_sample_tests()
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.test_queries = json.load(f)
        except Exception as e:
            print(f"Error loading test queries: {e}")
            self._create_sample_tests()

    def _create_sample_tests(self) -> None:
        """
        Create sample test queries for demonstration.
        """
        self.test_queries = [
            {
                "query": "What are the council bylaws?",
                "expected_domains": ["by-laws"],
                "expected_chunks": ["bylaws.txt"],
                "relevance_threshold": 0.7
            },
            {
                "query": "How do I pay my bills?",
                "expected_domains": ["billing"],
                "expected_chunks": ["bill_payments.txt"],
                "relevance_threshold": 0.7
            },
            {
                "query": "What licenses do I need?",
                "expected_domains": ["licensing"],
                "expected_chunks": ["operating_licenses.txt"],
                "relevance_threshold": 0.7
            },
            {
                "query": "Are there any public notices?",
                "expected_domains": ["notices"],
                "expected_chunks": ["public_notices.txt"],
                "relevance_threshold": 0.7
            }
        ]

    def evaluate_retrieval(self, n_results: int = 5) -> Dict[str, Any]:
        """
        Run evaluation on all test queries.

        Args:
            n_results: Number of results to retrieve per query

        Returns:
            Evaluation results summary
        """
        self.evaluation_results = []

        for test_query in self.test_queries:
            result = self._evaluate_single_query(test_query, n_results)
            self.evaluation_results.append(result)

        # Calculate overall metrics
        summary = self._calculate_metrics()
        return summary

    def _evaluate_single_query(self, test_query: Dict, n_results: int) -> Dict[str, Any]:
        """
        Evaluate a single test query.
        """
        query = test_query["query"]
        expected_domains = test_query.get("expected_domains", [])
        expected_chunks = test_query.get("expected_chunks", [])
        threshold = test_query.get("relevance_threshold", 0.5)

        # Determine query domain if classifier available
        predicted_domain = None
        if self.domain_classifier:
            predicted_domain = self.domain_classifier.classify_query(query)

        # Perform retrieval
        search_results = self.vector_db.search(query, n_results=n_results)

        retrieved_docs = search_results.get("documents", [[]])[0]
        retrieved_metadatas = search_results.get("metadatas", [[]])[0]
        retrieved_distances = search_results.get("distances", [[]])[0]
        retrieved_ids = search_results.get("ids", [[]])[0] if "ids" in results else []

        # Calculate metrics
        precision, recall, f1, relevance_scores = self._calculate_query_metrics(
            retrieved_metadatas, expected_domains, expected_chunks, threshold
        )

        result = {
            "query": query,
            "predicted_domain": predicted_domain,
            "expected_domains": expected_domains,
            "retrieved_chunks": len(retrieved_docs),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "avg_relevance": np.mean(relevance_scores) if relevance_scores else 0,
            "retrieved_details": [
                {
                    "id": chunk_id,
                    "domain": meta.get("domain", "unknown"),
                    "title": meta.get("title", "unknown"),
                    "distance": distance,
                    "content_preview": doc[:200] + "..." if len(doc) > 200 else doc
                }
                for chunk_id, meta, distance, doc in zip(
                    retrieved_ids, retrieved_metadatas, retrieved_distances, retrieved_docs
                )
            ]
        }

        return result

    def _calculate_query_metrics(self, retrieved_metadatas: List[Dict],
                               expected_domains: List[str],
                               expected_chunks: List[str],
                               threshold: float) -> Tuple[float, float, float, List[float]]:
        """
        Calculate precision, recall, and F1 score for a query.
        """
        if not retrieved_metadatas:
            return 0.0, 0.0, 0.0, []

        relevance_scores = []
        true_positives = 0
        retrieved_relevant = 0

        for metadata in retrieved_metadatas:
            chunk_domain = metadata.get("domain", "unknown")
            chunk_title = metadata.get("title", "unknown")

            # Calculate relevance score
            domain_match = chunk_domain in expected_domains if expected_domains else True
            chunk_match = any(expected in chunk_title for expected in expected_chunks) if expected_chunks else True

            relevance = 1.0 if (domain_match and chunk_match) else 0.0
            relevance_scores.append(relevance)

            if relevance >= threshold:
                retrieved_relevant += 1
                if domain_match or chunk_match:
                    true_positives += 1

        # Calculate metrics
        total_retrieved = len(retrieved_metadatas)
        total_expected = len(expected_domains) + len(expected_chunks)  # Approximate

        precision = true_positives / total_retrieved if total_retrieved > 0 else 0.0
        recall = true_positives / total_expected if total_expected > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return precision, recall, f1, relevance_scores

    def _calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate overall evaluation metrics.
        """
        if not self.evaluation_results:
            return {}

        total_queries = len(self.evaluation_results)
        avg_precision = np.mean([r["precision"] for r in self.evaluation_results])
        avg_recall = np.mean([r["recall"] for r in self.evaluation_results])
        avg_f1 = np.mean([r["f1_score"] for r in self.evaluation_results])
        avg_relevance = np.mean([r["avg_relevance"] for r in self.evaluation_results])

        # Domain classification accuracy
        domain_accuracy = 0
        if self.domain_classifier:
            correct_domains = 0
            for result in self.evaluation_results:
                pred_domain = result.get("predicted_domain")
                expected_domains = result.get("expected_domains", [])
                if pred_domain and expected_domains and pred_domain in expected_domains:
                    correct_domains += 1
            domain_accuracy = correct_domains / total_queries if total_queries > 0 else 0

        return {
            "total_queries": total_queries,
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f1_score": avg_f1,
            "average_relevance": avg_relevance,
            "domain_classification_accuracy": domain_accuracy,
            "detailed_results": self.evaluation_results
        }

    def save_results(self, output_file: str = "evaluation_results.json") -> None:
        """
        Save evaluation results to a JSON file.
        """
        filepath = os.path.join(os.path.dirname(__file__), "..", output_file)

        # Calculate summary
        summary = self._calculate_metrics()

        # Combine summary and detailed results
        output = {
            "summary": summary,
            "timestamp": str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now()),
            "detailed_results": self.evaluation_results
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Evaluation results saved to {filepath}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def print_summary(self) -> None:
        """
        Print a summary of evaluation results.
        """
        if not self.evaluation_results:
            print("No evaluation results available. Run evaluate_retrieval() first.")
            return

        summary = self._calculate_metrics()

        print("\n" + "="*60)
        print("RETRIEVAL EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Queries Evaluated: {summary['total_queries']}")
        print(".3f")
        print(".3f")
        print(".3f")
        print(".3f")

        if 'domain_classification_accuracy' in summary:
            print(".3f")

        print("\nTop Performing Queries:")
        sorted_results = sorted(self.evaluation_results,
                              key=lambda x: x['f1_score'], reverse=True)
        for i, result in enumerate(sorted_results[:3]):
            print(f"{i+1}. F1: {result['f1_score']:.3f} - {result['query'][:50]}...")

        print("\nQueries Needing Improvement:")
        worst_results = sorted(self.evaluation_results,
                             key=lambda x: x['f1_score'])
        for i, result in enumerate(worst_results[:3]):
            print(f"{i+1}. F1: {result['f1_score']:.3f} - {result['query'][:50]}...")