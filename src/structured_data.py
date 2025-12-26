"""
Structured data handler for JSON and SQL data integration.
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
import pandas as pd


class StructuredDataHandler:
    """
    Handles loading and processing of structured data (JSON, SQL tables).
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the structured data handler.

        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.structured_data = {}

    def load_json_files(self) -> Dict[str, List[Dict]]:
        """
        Load all JSON files from the data directory.

        Returns:
            Dictionary mapping filenames to list of records
        """
        json_data = {}

        if not os.path.exists(self.data_dir):
            return json_data

        for filename in os.listdir(self.data_dir):
            if filename.lower().endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Ensure data is a list of dictionaries
                        if isinstance(data, list):
                            json_data[filename] = data
                        elif isinstance(data, dict):
                            # Convert single dict to list
                            json_data[filename] = [data]
                        else:
                            print(f"Warning: {filename} contains unsupported JSON structure")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        self.structured_data.update(json_data)
        return json_data

    def load_sql_tables(self, db_path: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Load data from SQLite database tables.

        Args:
            db_path: Path to SQLite database file

        Returns:
            Dictionary mapping table names to list of records
        """
        sql_data = {}

        if not db_path:
            # Look for .db or .sqlite files in data directory
            for filename in os.listdir(self.data_dir):
                if filename.lower().endswith(('.db', '.sqlite', '.sqlite3')):
                    db_path = os.path.join(self.data_dir, filename)
                    break

        if not db_path or not os.path.exists(db_path):
            return sql_data

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            for table_name, in tables:
                # Skip system tables
                if table_name.startswith('sqlite_'):
                    continue

                # Load table data
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                records = df.to_dict('records')
                sql_data[table_name] = records

            conn.close()

        except Exception as e:
            print(f"Error loading SQL database: {e}")

        self.structured_data.update(sql_data)
        return sql_data

    def convert_to_documents(self, domain_classifier=None) -> List[Dict]:
        """
        Convert structured data to document format for vector database.

        Args:
            domain_classifier: Optional domain classifier for assigning domains

        Returns:
            List of documents in the format expected by VectorDB
        """
        documents = []

        for source_name, records in self.structured_data.items():
            if not records:
                continue

            # Determine domain
            domain = "structured"
            if domain_classifier:
                domain = domain_classifier.classify_document(source_name)

            # Convert records to text documents
            for i, record in enumerate(records):
                # Create a readable text representation
                content_parts = []
                for key, value in record.items():
                    if value is not None:
                        content_parts.append(f"{key}: {value}")

                content = "\n".join(content_parts)

                # Create metadata
                metadata = {
                    "source": source_name,
                    "domain": domain,
                    "record_id": f"{source_name}_{i}",
                    "data_type": "structured"
                }

                documents.append({
                    "content": content,
                    "metadata": metadata
                })

        return documents

    def search_structured_data(self, query: str, domain: Optional[str] = None) -> List[Dict]:
        """
        Search structured data using simple text matching.

        Args:
            query: Search query
            domain: Optional domain filter

        Returns:
            List of matching records
        """
        results = []
        query_lower = query.lower()

        for source_name, records in self.structured_data.items():
            # Check domain filter
            current_domain = "structured"
            if domain and current_domain != domain:
                continue

            for record in records:
                # Simple text search in record values
                record_text = " ".join(str(v) for v in record.values() if v is not None).lower()
                if query_lower in record_text:
                    results.append({
                        "record": record,
                        "source": source_name,
                        "domain": current_domain
                    })

        return results

    def get_all_data(self) -> Dict[str, List[Dict]]:
        """
        Get all loaded structured data.
        """
        return self.structured_data.copy()