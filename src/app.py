import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from vectordb import VectorDB
from conversation import format_history
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import yaml

# Load environment variables
load_dotenv()


def load_documents() -> List[Dict]:
    """
    Load documents for demonstration.

    Returns:
        List of documents as dicts with 'content' and 'metadata'
    """
    results = []
    data_dir = "data"
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' does not exist.")
        import yaml
        return results

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        if os.path.isfile(filepath) and filename.lower().endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                results.append({
                    "content": content,
                    "metadata": {"title": filename}
                })
    return results


class RAGAssistant:
    """
    A simple RAG-based AI assistant using ChromaDB and multiple LLM providers.
    Supports OpenAI, Groq, and Google Gemini APIs.
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

        # Load prompt from YAML config
        prompt_path = os.path.join(os.path.dirname(__file__), '../config/prompt_config.yaml')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        prompt_str = config.get('rag_assistant_prompt', '')

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

        print("RAG Assistant initialized successfully")

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

    def invoke(self, input: str, n_results: int = 3, history: List[Dict[str, str]] = None) -> str:
        """
        Query the RAG assistant.

        Args:
            input: User's input
            n_results: Number of relevant chunks to retrieve
            history: List of previous turns (user/assistant)

        Returns:
            String answer from the LLM
        """
        # Retrieve relevant chunks from vector DB
        search_results = self.vector_db.search(input, n_results=n_results)
        documents = search_results.get("documents", [[]])[0]  # Get the first (and only) list of documents

        # Combine retrieved chunks into context string
        context = "\n\n".join(documents)

        # Format conversation history
        history_str = format_history(history or [])

        # Prepare prompt input
        prompt_input = {
            "context": context,
            "question": input,
            "history": history_str,
        }

        # Update prompt template to include history if not already
        # (You may want to update self.prompt_template to use {history} in the template string)
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

        assistant.add_documents(sample_docs)

        done = False

        while not done:
            question = input("Enter a question or 'quit' to exit: ")
            if question.lower() == "quit":
                done = True
            else:
                result = assistant.invoke(question)
                print(result)

    except Exception as e:
        print(f"Error running RAG assistant: {e}")
        print("Make sure you have set up your .env file with at least one API key:")
        print("- OPENAI_API_KEY (OpenAI GPT models)")
        print("- GROQ_API_KEY (Groq Llama models)")
        print("- GOOGLE_API_KEY (Google Gemini models)")


if __name__ == "__main__":
    main()

