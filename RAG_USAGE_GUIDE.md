# RAG Q&A System - Usage Guide

## Overview
The AI Research Agent now includes a RAG (Retrieval Augmented Generation) system that allows you to ask questions about your research PDFs without reading the entire document. The system uses:

- **PDF Text Extraction**: Automatically extracts text from generated research reports
- **Smart Chunking**: Splits documents into 600-character overlapping segments for better retrieval
- **TF-IDF Retrieval**: Finds the most relevant sections using TF-IDF vectorization
- **Groq Integration**: Uses Groq API (llama-3.3-70b-versatile) to answer questions based on document context
- **Chat History**: Stores all conversations in MongoDB with full context preservation

## Workflow

### 1. Generate Research Report
```bash
POST /api/research
Authorization: Bearer <your_token>

{
  "query": "artificial intelligence trends"
}

Response includes:
{
  "pdf_filename": "research_report_20260418_143245.pdf",
  "pdf_path": "/path/to/reports/research_report_20260418_143245.pdf",
  ...
}
```

### 2. Ask Questions About the PDF
```bash
POST /api/chat/ask
Authorization: Bearer <your_token>

{
  "question": "What are the latest trends in AI?",
  "pdf_filename": "research_report_20260418_143245.pdf"
}

Response:
{
  "answer": "Based on the research document, the latest AI trends include...",
  "sources": [
    {
      "text": "[Source 1 - Relevance: 0.85] Machine learning advances...",
      "relevance": 0.85
    },
    {
      "text": "[Source 2 - Relevance: 0.78] Deep learning applications...",
      "relevance": 0.78
    }
  ],
  "confidence": 0.85,
  "timestamp": "2026-04-18T14:32:45"
}
```

### 3. Retrieve Chat History
```bash
GET /api/chat/history?pdf_filename=research_report_20260418_143245.pdf
Authorization: Bearer <your_token>

Response:
{
  "pdf_filename": "research_report_20260418_143245.pdf",
  "conversation": [
    {
      "role": "user",
      "content": "What are the trends?",
      "timestamp": "2026-04-18T14:32:45"
    },
    {
      "role": "assistant",
      "content": "The trends include...",
      "timestamp": "2026-04-18T14:32:46"
    }
  ],
  "message_count": 2,
  "created_at": "2026-04-18T14:32:45",
  "updated_at": "2026-04-18T14:32:46"
}
```

### 4. View All Chat Sessions
```bash
GET /api/chat/sessions
Authorization: Bearer <your_token>

Response:
{
  "sessions": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "username": "john_doe",
      "pdf_filename": "research_report_20260418_143245.pdf",
      "message_count": 8,
      "created_at": "2026-04-18T14:32:45",
      "updated_at": "2026-04-18T14:35:20"
    }
  ],
  "total": 1
}
```

### 5. Delete Chat Session
```bash
DELETE /api/chat/session?pdf_filename=research_report_20260418_143245.pdf
Authorization: Bearer <your_token>

Response:
{
  "message": "Chat session deleted successfully"
}
```

## System Architecture

### RAG Engine (tools/rag_engine.py)
```python
from tools.rag_engine import RAGEngine

engine = RAGEngine(chunk_size=600, chunk_overlap=150)
engine.build_index(pdf_path)

# Retrieve relevant context
chunks = engine.retrieve_relevant_chunks(query, top_k=5)

# Build context for LLM
context = engine.build_context(query, top_k=5)
```

**Key Methods:**
- `extract_pdf_text(pdf_path)` - Extract full text from PDF
- `chunk_text(text)` - Split text into overlapping chunks
- `build_index(pdf_path)` - Create searchable index
- `retrieve_relevant_chunks(query, top_k)` - Find most relevant sections
- `build_context(query, top_k)` - Prepare context for LLM

### Q&A Agent (agents/qa_agent.py)
```python
from agents.qa_agent import answer_question, summarize_conversation

result = answer_question(
    question="What are the key findings?",
    context="Retrieved document context...",
    chat_history=[...]  # Optional previous messages
)

# Returns: {answer, confidence, tokens_used}
```

## Chat Data Storage

### MongoDB chat_sessions Collection
```javascript
{
  "_id": ObjectId,
  "username": "john_doe",
  "pdf_filename": "research_report_20260418_143245.pdf",
  "pdf_path": "/path/to/reports/research_report_20260418_143245.pdf",
  "conversation": [
    {
      "role": "user",
      "content": "What are the key findings?",
      "timestamp": ISODate
    },
    {
      "role": "assistant",
      "content": "The key findings are...",
      "timestamp": ISODate
    }
  ],
  "created_at": ISODate,
  "updated_at": ISODate,
  "message_count": 6
}
```

## How RAG Works

### 1. Document Processing
```
PDF → Extract Text → Create Chunks → TF-IDF Vectorization → Store Index
```

### 2. Query Processing
```
Question → Vectorize → Find Similar Chunks → Rank by Relevance → Top-K Results
```

### 3. Answer Generation
```
Question + Context → Groq API → LLM Answer → Store in Chat History
```

## Features

### Smart Chunking
- Chunks are 600 characters with 150-character overlap
- Preserves context across chunk boundaries
- Prevents losing important information at chunk edges

### Relevance Scoring
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Cosine similarity measurement
- Relevance scores 0-1 (only shows scores > 0)

### Context Window
- Retrieves top 5 most relevant chunks by default
- Includes relevance scores in context
- Formatted for LLM consumption

### Chat Memory
- Stores full conversation history
- Includes timestamps for all messages
- Tracks message count for analytics

### Confidence Scoring
- 0.85 if context is found and substantial (>100 chars)
- 0.5 if minimal context available
- Helps user understand answer reliability

## Example Usage Flow

```bash
# 1. Research a topic
curl -X POST http://localhost:7000/api/research \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning advances 2026"}'

# 2. Ask follow-up questions
curl -X POST http://localhost:7000/api/chat/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the most promising applications?",
    "pdf_filename": "research_report_20260418_143245.pdf"
  }'

# 3. Ask more questions (same session)
curl -X POST http://localhost:7000/api/chat/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How does this compare to previous years?",
    "pdf_filename": "research_report_20260418_143245.pdf"
  }'

# 4. Review entire conversation
curl http://localhost:7000/api/chat/history?pdf_filename=research_report_20260418_143245.pdf \
  -H "Authorization: Bearer <token>"
```

## Performance Notes

- **First Question**: Slightly slower (builds index first time)
- **Subsequent Questions**: Fast (uses cached index)
- **Index Remains**: In memory until RAG engine deleted
- **Clear Cache**: Delete chat session to free memory

## Error Handling

### Common Errors

1. **PDF not found**
   - Check pdf_filename matches exactly
   - Verify user owns the research

2. **No relevant context**
   - Question too specific for document
   - Try rephrasing question
   - Confidence score will be lower

3. **Token invalid**
   - Re-authenticate to get new token
   - Token expires after 30 minutes

## Future Enhancements

- Semantic search with embeddings (OpenAI, Hugging Face)
- Multi-document Q&A across multiple PDFs
- Document summarization endpoint
- Citation tracking with exact page numbers
- Advanced prompt engineering for better answers
