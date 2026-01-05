import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import VectorDB
from conversation import format_history
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import yaml

# Import new modules
from domain_classifier import DomainClassifier
from structured_data import StructuredDataHandler
from evaluation import RetrievalEvaluator

# Load environment variables
load_dotenv()


def load_documents() -> List[Dict]:
    """
    Load documents for demonstration with domain classification and structured data support.

    Returns:
        List of documents as dicts with 'content' and 'metadata'
    """
    results = []
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' does not exist.")
        import yaml
        return results

    # Initialize domain classifier
    domain_classifier = DomainClassifier(use_embeddings=False)  # Use keyword matching for speed

    # Load text documents
    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

                # Classify document domain
                domain = domain_classifier.classify_document(filename)

                results.append({
                    "content": content,
                    "metadata": {
                        "title": filename,
                        "domain": domain,
                        "data_type": "text"
                    }
                })

    # Load structured data
    structured_handler = StructuredDataHandler(data_dir)
    structured_handler.load_json_files()
    structured_handler.load_sql_tables()

    structured_docs = structured_handler.convert_to_documents(domain_classifier)
    results.extend(structured_docs)

    return results


class RAGAssistant:
    """
    A simple RAG-based AI assistant using ChromaDB and multiple LLM providers.
    Supports OpenAI, Groq, and Google Gemini APIs.
    Enhanced with domain classification and structured data support.
    """

    def __init__(self):
        """Initialize the RAG assistant."""
        # Initialize LLM - check for available API keys in order of preference
        self.llm = self._initialize_llm()
        if not self.llm:
            raise ValueError(
                "No valid API key found. Please set one of: "
                "OPENAI_API_KEY, GROQ_API_KEY, or GOOGLE_API_KEY in your .env file"
            )

        # Initialize vector database
        self.vector_db = VectorDB()

        # Initialize domain classifier
        self.domain_classifier = DomainClassifier(use_embeddings=False)

        # Initialize structured data handler
        self.structured_handler = StructuredDataHandler()

        # Load prompt from YAML config
        prompt_path = os.path.join(os.path.dirname(__file__), '../config/prompt_config.yaml')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            prompt_str = config.get('general_assistant_prompt', '')
            if not prompt_str:
                print(f"Warning: general_assistant_prompt not found in {prompt_path}, using default")
                prompt_str = "You are a helpful assistant for Masvingo City Council. Answer questions based on the provided context."
        except Exception as e:
            print(f"Warning: Failed to load prompt config from {prompt_path}: {e}, using default")
            prompt_str = "You are a helpful assistant for Masvingo City Council. Answer questions based on the provided context."

        # Add placeholders for history, context, and question
        prompt_template_str = (
            f"{prompt_str}\n\n"
            "Conversation history:\n{history}\n\n"
            "Context:\n{context}\n\n"
            "Question:\n{question}\n\n"
            "Answer:"
        )
        self.prompt_template = ChatPromptTemplate.from_template(prompt_template_str)

        # Create the chain
        self.chain = self.prompt_template | self.llm | StrOutputParser()

        print("RAG Assistant initialized successfully with domain classification and structured data support")

    def _initialize_llm(self):
        """
        Initialize the LLM by checking for available API keys.
        Tries OpenAI, Groq, and Google Gemini in that order.
        """
        

        if  os.getenv("GROQ_API_KEY"):
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            print(f"Using Groq model: {model_name}")
            return ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"), model=model_name, temperature=0.0
            )
        else:
            raise ValueError(
                "No valid API key found. Please setup GROQ_API_KEY your .env file"
            )

    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of documents
        """
        self.vector_db.add_documents(documents)

    def run_evaluation(self, n_results: int = 5) -> Dict[str, Any]:
        """
        Run retrieval evaluation on test queries.

        Args:
            n_results: Number of results to retrieve per query

        Returns:
            Evaluation results
        """
        evaluator = RetrievalEvaluator(self.vector_db, self.domain_classifier)
        evaluator.load_test_queries()
        results = evaluator.evaluate_retrieval(n_results=n_results)
        evaluator.save_results()
        evaluator.print_summary()
        return results

    def invoke(self, input: str, n_results: int = 3, history: List[Dict[str, str]] = None) -> str:
        """
        Query the RAG assistant with domain classification and structured data support.

        Args:
            input: User's input
            n_results: Number of relevant chunks to retrieve
            history: List of previous turns (user/assistant)

        Returns:
            String answer from the LLM
        """
        # Step 1: Classify query domain
        query_domain = self.domain_classifier.classify_query(input)
        print(f"Query classified as domain: {query_domain}")

        # Step 2: Retrieve relevant chunks from vector DB with domain filtering
        search_results = self.vector_db.search(input, n_results=n_results, domain_filter=query_domain)
        documents = search_results.get("documents", [[]])[0]  # Get the first (and only) list of documents

        # Step 3: Search structured data if available
        structured_results = self.structured_handler.search_structured_data(input, query_domain)

        # Step 4: Combine unstructured and structured context
        context_parts = []

        # Add unstructured text chunks
        if documents:
            text_context = "\n\n".join(documents)
            context_parts.append(f"Unstructured Information:\n{text_context}")

        # Add structured data results
        if structured_results:
            structured_context = ""
            for result in structured_results[:3]:  # Limit to top 3 structured results
                record = result["record"]
                record_text = "\n".join(f"{k}: {v}" for k, v in record.items())
                structured_context += f"\nSource: {result['source']}\n{record_text}\n"
            if structured_context:
                context_parts.append(f"Structured Data:\n{structured_context}")

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant information found."

        # Format conversation history
        history_str = format_history(history or [])

        # Prepare prompt input
        prompt_input = {
            "context": context,
            "question": input,
            "history": history_str,
        }

        # Generate answer
        answer = self.chain.invoke(prompt_input)

        return answer


def main():
    """Main function to demonstrate the RAG assistant."""
    try:
        # Initialize the RAG assistant
        print("Initializing RAG Assistant...")
        assistant = RAGAssistant()

        # Load sample documents
        print("\nLoading documents...")
        sample_docs = load_documents()
        print(f"Loaded {len(sample_docs)} sample documents")

        # Load structured data
        assistant.structured_handler.load_json_files()
        assistant.structured_handler.load_sql_tables()

        assistant.add_documents(sample_docs)

        print("\nAvailable commands:")
        print("- 'ask <question>' to query the assistant")
        print("- 'evaluate' to run retrieval evaluation")
        print("- 'domains' to list available domains")
        print("- 'quit' to exit")

        done = False

        while not done:
            user_input = input("\nEnter command: ").strip()

            if user_input.lower() == "quit":
                done = True
            elif user_input.lower() == "evaluate":
                print("\nRunning retrieval evaluation...")
                assistant.run_evaluation()
            elif user_input.lower() == "domains":
                domains = assistant.domain_classifier.get_available_domains()
                print(f"\nAvailable domains: {', '.join(domains)}")
            elif user_input.lower().startswith("ask "):
                question = user_input[4:].strip()
                if question:
                    result = assistant.invoke(question)
                    print(f"\nAnswer: {result}")
                else:
                    print("Please provide a question after 'ask'")
            else:
                print("Unknown command. Use 'ask <question>', 'evaluate', 'domains', or 'quit'")

    except Exception as e:
        print(f"Error running RAG assistant: {e}")
        print("Make sure you have set up your .env file with at least one API key:")
        print("- OPENAI_API_KEY (OpenAI GPT models)")
        print("- GROQ_API_KEY (Groq Llama models)")
        print("- GOOGLE_API_KEY (Google Gemini models)")


if __name__ == "__main__":
    main()

