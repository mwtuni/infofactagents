# InfoGenAI - Zero-shot News Article Trustworthiness Classifier

**InfoGenAI** is a powerful, AI-driven tool designed to classify and assess the trustworthiness of news articles in real-time. It leverages advanced large language models (LLMs) and retrieval-augmented generation (RAG) techniques to evaluate articles based on a variety of factors, including factual accuracy, bias detection, and source credibility, all without requiring any training data specific to the articles at hand. **InfoGenAI** uses multiple specialized agents to classify and score news articles on their reliability.

## Architecture Overview

![InfoGenAI Architecture](path_to_image)

### Front-End Components
The front-end consists of multiple user interfaces, making it easy to interact with the classification system:

- **Gradio Interface**: A web-based interface that allows users to submit news articles and receive detailed trustworthiness scores and explanations. Accessible through any web browser. [Open in Colab](#)
  
- **API Integration**: The backend provides a RESTful API for integration with other platforms, allowing news articles to be classified programmatically.

These front-end channels facilitate communication between the user and the back-end components, ensuring a smooth user experience.

### Back-End Components
The back-end is responsible for processing the articles, managing data, and handling the AI-powered classification:

- **Python**: The primary programming language used for backend logic and integration with various AI components.
  
- **Flask**: A lightweight WSGI web framework that serves as the backbone for API creation, handling the communication between front-end and back-end.
  
- **InfoGenAI Models**: The core AI components that classify news articles based on various agents (metadata evaluation, factual consistency, linguistic analysis, etc.).
  
- **Ollama**: A platform for running local large language models (LLMs) securely, ensuring that all data processing remains within a private environment.

- **Retrieval-Augmented Generation (RAG)**: Used to enhance the AI's understanding by retrieving and comparing facts from external, trusted databases to verify claims made in the article.

### Specialized Agents
InfoGenAI uses multiple specialized agents to evaluate and classify the news articles based on different criteria:

- **Metadata & Source Credibility Agent**: Analyzes the article's metadata (e.g., publication date, author credentials, source reliability) to assess the overall credibility of the news source.
  
- **Factual Consistency Agent**: Verifies the factual accuracy of the claims made within the article, cross-referencing them against trusted external databases using **RAG**.
  
- **Bias & Sentiment Analysis Agent**: Evaluates the article for potential bias or sensationalism, assessing the tone and sentiment of the content to ensure neutrality and objectivity.

- **Linguistic Analysis Agent**: Performs deep linguistic analysis to identify misleading language, word choice, or other subtle indicators of biased reporting.

Each of these agents works independently to evaluate different aspects of the article, providing a comprehensive trustworthiness score and a detailed breakdown of findings.

### Data Flow and Communication
1. **User Input**: Users submit news articles via the Gradio interface or through API calls.
  
2. **Article Classification**: 
   - The Flask backend processes the request.
   - The article is sent to multiple specialized agents (Metadata & Source Credibility, Factual Consistency, Bias & Sentiment Analysis, Linguistic Analysis) for evaluation.
   - **Ollama** is used for processing private data locally, and **RAG** retrieves trusted external sources to verify claims in the article.
  
3. **Result Generation**: After classification, the AI generates a trustworthiness score and a detailed explanation of the assessment.
  
4. **Response Delivery**: The result is sent back to the user through the Gradio interface or the API.

### Security and Privacy Considerations
- **Data Privacy**: The system ensures that all user interactions remain private. **Ollama** allows for local model execution, so user data is processed within a secure environment.
  
- **No External Data Access**: All data processing happens on local servers, ensuring that sensitive information is never sent to external sources.

### Technologies Summary

| Component                          | Role                                                | Technology                |
|-------------------------------------|-----------------------------------------------------|---------------------------|
| **Gradio**                          | Web Interface for User Interaction                  | Gradio Library            |
| **Flask**                           | Web Framework for API & Backend Logic               | Flask                     |
| **Python**                          | Core Backend Logic                                  | Python Programming        |
| **Ollama**                          | Local AI Model Execution                            | Ollama                    |
| **RAG**                             | Retrieval-Augmented Generation                      | Custom RAG Implementation |
| **API**                             | Communication Gateway                                | Flask API                 |
  
### Data Flow Summary
1. **User submits** a news article through Gradio or the API.
2. The **Flask server** processes the article and sends it to different specialized agents for classification (e.g., metadata evaluation, factual verification, sentiment analysis).
3. The agents process the article, accessing local models via **Ollama** and trusted data sources via **RAG**.
4. **Trustworthiness scores and explanations** are generated and sent back to the user.
5. The results are presented via the **Gradio interface** or the API, depending on the user's interaction method.

This architecture enables **InfoGenAI** to perform zero-shot classification of news articles, analyzing their trustworthiness without requiring pre-labeled datasets. It ensures privacy, reliability, and flexibility in evaluating news content.
