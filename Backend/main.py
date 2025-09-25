import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
from pypdf import PdfReader

load_dotenv()
# Load HuggingFace embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Init Chroma DB with persistent storage
chroma_db_path = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=chroma_db_path)
collection = chroma_client.get_or_create_collection(name="docs")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# FastAPI app
app = FastAPI(title="Mini RAG App with PDF Support + Doc Filtering")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper: Extract text from PDF
def extract_text_from_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# 1. Upload PDF & store embeddings (with auto-generated doc_id)
@app.post("/upload")
async def upload_document(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        return JSONResponse({"error": "Only PDF files are supported"}, status_code=400)

    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    text = extract_text_from_pdf(file)

    chunk_size = 1000
    overlap = 200
    chunks = []
    
    # Process the entire document text
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk.strip())
    
    # Ensure we process ALL chunks from the document
    print(f"Processing {len(chunks)} chunks from document: {file.filename}")
    
    # Store each chunk in the database
    for idx, chunk in enumerate(chunks):
        try:
            emb = embedding_model.encode(chunk).tolist()
            collection.add(
                ids=[f"{doc_id}_{idx}"],
                embeddings=[emb],
                documents=[chunk],
                metadatas=[{"doc_id": doc_id, "filename": file.filename, "chunk_index": idx}]
            )
            print(f"Stored chunk {idx + 1}/{len(chunks)}")
        except Exception as e:
            print(f"Error storing chunk {idx}: {e}")
            continue

    return {
        "message": f"Successfully stored ALL {len(chunks)} chunks from {file.filename}",
        "doc_id": doc_id,
        "total_chunks": len(chunks),
        "document_length": len(text)
    }

# 2. Ask question (RAG with doc_id filter)
@app.post("/ask")
async def ask_question(question: str = Form(...), doc_id: str = Form(...)):
    q_emb = embedding_model.encode(question).tolist()

    # Retrieve more chunks for better context
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=5,  # Increased from 3 to 5 for more comprehensive results
        where={"doc_id": doc_id}  # filter by doc_id
    )

    if not results["documents"] or not results["documents"][0]:
        return JSONResponse({"answer": f"No content found for document {doc_id}"})

    context = " ".join(results["documents"][0])

    # Use Gemini 1.5 Flash (more reliable free model)
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    # Enhanced prompt for better document analysis
    prompt = f"""You are an expert document analyst. Analyze the document content and provide a comprehensive, well-structured answer.

**DOCUMENT CONTENT:**
{context}

**QUESTION:** {question}

**ANALYSIS INSTRUCTIONS:**
1. **Extract Key Information**: Identify the most relevant information from the document that directly answers the question
2. **Provide Specific Details**: Include specific facts, numbers, dates, names, or quotes from the document
3. **Structure Your Response**: Use clear markdown formatting with headers, bullet points, and emphasis
4. **Be Comprehensive**: Don't just give a brief answer - provide context and supporting details
5. **Cite Sources**: When possible, reference specific sections or parts of the document

**RESPONSE FORMAT:**
- Start with a direct answer to the question
- Use **Key Points** section for main findings
- Include **Supporting Details** with specific information
- Add **Additional Context** if relevant
- Use bullet points, bold text, and proper formatting

**If the question is not relevant to the document:**
**Not Relevant**
This question is not related to the document content. Please ask a question about the document.

**If insufficient information is found:**
**Insufficient Information**
I cannot find enough information in the document to answer this question accurately.

**If no content is available:**
**No Content**
No relevant content found in the document to answer your question.

Provide your analysis in markdown format:"""
    
    response = model.generate_content(prompt)

    return JSONResponse({
        "doc_id": doc_id,
        "answer": response.text
    })
