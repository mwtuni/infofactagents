# 🧠 InfoFactAgents – AI-Powered News Trustworthiness Analyzer

**InfoFactAgents** is a zero-shot, multi-agent framework that evaluates the **trustworthiness of news articles** using large language models (LLMs), retrieval-augmented generation (RAG), and fact-checking tools. It requires no training data and delivers detailed analyses via a web interface or REST API.

---

## 🚀 Features

- 🔍 **Multiple Evaluation Agents** (sentiment, metadata, factual accuracy)
- 🧠 **LLM-Powered Analysis** (GPT-3.5/GPT-4o)
- 🔄 **RAG-style Contextual Reasoning**
- 🌐 **Gradio Interface + REST API**
- 🧪 **Zero-Shot Classification** (no pre-labeling needed)

---

## 🧱 Architecture Overview

### Frontend

- **Gradio UI**: Submit articles or URLs, select evaluation agents, and view analysis.
- **Debug Panel**: Inspect request/response logs for troubleshooting.
- **Authentication**: Optional login via environment variables.

### Backend

- **Flask API**: Receives article input, manages sessions, routes data to agents.
- **Agent Manager**: Dynamically loads all Python agents from the `agents/` folder.
- **System Prompt Generator**: Auto-builds LLM prompts based on available agents.

---

## 🧠 Evaluation Agents

Each agent is a standalone class with a `process_article(text)` method.

| Agent                     | Description |
|---------------------------|-------------|
| `sentiment_analysis_agent` | Analyzes emotional tone and sentiment bias. |
| `metadata_agent`           | Evaluates credibility of URLs and named persons. |
| `factual_consistency_agent` | Extracts claims, verifies with LLM and Google Fact Check API. |

All results are returned in Markdown format with added icons for clarity.

---

## 🔄 Data Flow Summary

1. **User submits** an article or URL via Gradio or API.
2. **Backend loads** the selected agents.
3. **Each agent processes** the article independently.
4. **RAG combines** the outputs into a unified trustworthiness report.
5. **Response is sent** back to the user.

---

## 🛠️ Technologies

| Component      | Tech Used           |
|----------------|---------------------|
| UI             | Gradio              |
| Backend API    | Flask               |
| LLMs           | OpenAI (GPT)        |
| Fact-checking  | Google Fact Check API |
| Auth           | Environment variables |
| Agent Loading  | Dynamic with `importlib` |
