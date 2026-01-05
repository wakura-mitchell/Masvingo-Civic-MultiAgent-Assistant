

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import time
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent))  # Add masvingo_civic_assistant
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))  # Add src for backward compatibility

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../data')
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')  # Set a secure key in production

# Enable CORS for all routes
CORS(app)

# Lazy initialization of RAG assistant
rag_assistant = None

def get_rag_assistant():
    global rag_assistant
    if rag_assistant is None:
        print("Initializing RAG Assistant...")
        # Import from the src directory explicitly
        import os
        src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'app.py')
        print(f"Loading RAG from: {src_path}")
        import importlib.util
        spec = importlib.util.spec_from_file_location("src_app", src_path)
        src_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(src_app)
        
        RAGAssistant = src_app.RAGAssistant
        load_documents = src_app.load_documents
        
        rag_assistant = RAGAssistant()
        print("Loading documents...")
        sample_docs = load_documents()
        print(f"Loaded {len(sample_docs)} documents")
        rag_assistant.add_documents(sample_docs)
        print("RAG Assistant ready!")
    return rag_assistant

# Lazy initialization of Coordinator Agent
coordinator_agent = None

def get_coordinator_agent():
    global coordinator_agent
    if coordinator_agent is None:
        print("Initializing Coordinator Agent...")
        from agents.coordinator_agent import CoordinatorAgent
        # Use LangGraph for proper agent orchestration
        coordinator_agent = CoordinatorAgent(use_langgraph=True)
        print("Coordinator Agent ready!")
    return coordinator_agent

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    question = request.form.get("question")
    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Get or initialize conversation history from session
    history = session.get('history', [])

    try:
        # Get RAG assistant (lazy initialization)
        assistant = get_rag_assistant()
        # Pass history to RAG assistant (update RAGAssistant to accept history if needed)
        answer = assistant.invoke(question, history=history)
        # Update history
        history.append({"user": question, "assistant": answer})
        session['history'] = history
        return jsonify({"answer": answer, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        # Ingest the new document
        try:
            assistant = get_rag_assistant()
            with open(save_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc = {"content": content, "metadata": {"title": filename}}
            assistant.vector_db.add_documents([doc])
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "File type not allowed."}), 400

@app.route("/agents")
def agents():
    return render_template("agent_interface.html")

@app.route("/agent-query", methods=["POST"])
def agent_query():
    question = request.form.get("question", "")
    files = request.files.getlist("files") if "files" in request.files else []

    if not question and not files:
        return jsonify({"error": "No question or files provided."}), 400

    try:
        # Process uploaded files if any
        file_contents = []
        if files:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    content = file.read().decode('utf-8', errors='ignore')
                    file_contents.append({
                        "filename": filename,
                        "content": content,
                        "type": file.content_type
                    })
                else:
                    return jsonify({"error": f"File type not allowed for {file.filename}."}), 400

        # Combine question with file contents
        full_query = question
        if file_contents:
            file_summaries = [f"Content from {f['filename']}: {f['content'][:500]}..." for f in file_contents]
            full_query += "\n\nAttached files:\n" + "\n".join(file_summaries)

        print(f"Processing query: {full_query[:100]}...")
        agent = get_coordinator_agent()
        start_time = time.time()
        
        # Check if this is likely an unknown query that should use RAG
        query_lower = full_query.lower()
        is_unknown_query = not any(word in query_lower for word in [
            "bill", "payment", "balance", "water", "owe", "pay",
            "pipe", "burst", "leak", "incident", "report",
            "license", "licence", "permit", "application", "form"
        ])
        
        if is_unknown_query:
            # Try RAG tool directly for unknown queries
            try:
                from tools.rag_tool import RAGTool
                rag_tool = RAGTool()
                answer = rag_tool.query(full_query, include_web=True)
                agent_type = "unknown"
                print("Used RAG tool for unknown query")
            except Exception as rag_e:
                print(f"RAG tool failed: {rag_e}, falling back to coordinator")
                answer = agent.route_query(full_query)
                agent_type = "unknown"
        else:
            answer = agent.route_query(full_query)
            agent_type = "unknown"  # Will be overridden below
        
        response_time = time.time() - start_time

        # Determine agent type based on question content (simplified classification)
        query_lower = (question + " " + " ".join([f['content'] for f in file_contents])).lower()
        if any(word in query_lower for word in ["bill", "payment", "balance", "water"]):
            agent_type = "billing"
        elif any(word in query_lower for word in ["pipe", "burst", "leak", "incident", "report"]):
            agent_type = "incident"
        elif any(word in query_lower for word in ["license", "licence", "permit", "application"]):
            agent_type = "licensing"
        # Keep agent_type as "unknown" if it wasn't changed above

        return jsonify({
            "answer": answer,
            "response": answer,
            "agent_used": agent_type,
            "classification": agent_type,
            "response_time": round(response_time, 2),
            "files_processed": len(file_contents)
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in agent_query: {e}")
        print(f"Traceback: {error_details}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/orchestrated-query", methods=["POST"])
def orchestrated_query():
    """Enhanced endpoint that provides detailed agent routing information."""
    question = request.form.get("question")
    if not question:
        return jsonify({"error": "No question provided."}), 400

    try:
        agent = get_coordinator_agent()
        start_time = time.time()
        answer = agent.route_query(question)
        response_time = time.time() - start_time

        # Determine agent type based on question content (simplified classification)
        agent_type = "unknown"
        if any(word in question.lower() for word in ["bill", "payment", "balance", "water"]):
            agent_type = "billing"
        elif any(word in question.lower() for word in ["pipe", "burst", "leak", "incident", "report"]):
            agent_type = "incident"
        elif any(word in question.lower() for word in ["license", "licence", "permit", "application"]):
            agent_type = "licensing"

        return jsonify({
            "answer": answer,
            "response": answer,
            "agent_used": agent_type,
            "classification": agent_type,
            "response_time": round(response_time, 2),
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/agent-status", methods=["GET"])
def agent_status():
    """Get current status of all agents."""
    try:
        # This would ideally check actual agent health
        # For now, return mock status
        status = {
            "billing": {"status": "online", "response_time": "2.1s", "queries_today": 15},
            "incident": {"status": "online", "response_time": "3.2s", "queries_today": 8},
            "licensing": {"status": "online", "response_time": "5.1s", "queries_today": 12},
            "general": {"status": "online", "response_time": "4.0s", "queries_today": 23},
            "system": {"status": "healthy", "uptime": "2h 15m", "total_queries": 58}
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/system-health", methods=["GET"])
def system_health():
    """Get overall system health metrics."""
    try:
        return jsonify({
            "status": "healthy",
            "agents": {
                "coordinator": "online",
                "billing": "online",
                "incident": "online",
                "licensing": "online",
                "general": "online"
            },
            "services": {
                "database": "online",
                "vector_store": "online",
                "api_endpoints": "online"
            },
            "metrics": {
                "total_queries": 156,
                "avg_response_time": "3.5s",
                "uptime": "99.8%"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
