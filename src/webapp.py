

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../data')
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__, template_folder="templates")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretkey')  # Set a secure key in production

# Lazy initialization of RAG assistant
rag_assistant = None

def get_rag_assistant():
    global rag_assistant
    if rag_assistant is None:
        print("Initializing RAG Assistant...")
        from app import RAGAssistant, load_documents
        rag_assistant = RAGAssistant()
        print("Loading documents...")
        sample_docs = load_documents()
        print(f"Loaded {len(sample_docs)} documents")
        rag_assistant.add_documents(sample_docs)
        print("RAG Assistant ready!")
    return rag_assistant

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

if __name__ == "__main__":
    app.run(debug=True)
