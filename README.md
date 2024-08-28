# Project Setup Guide

## Prerequisites

- Ensure you have Docker and Docker Compose installed on your machine.
- Python 3.7 or higher installed.

- **Install Ollama**: Follow the instructions to install Ollama on your machine. You can download it from [Ollama's official website](https://ollama.com). For Linux users, you can run:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Pull Models**: After installing Ollama, you can pull the models you want to use. For example, to pull the Llama2 model, run:
  ```bash
  ollama pull llama3.1:8b
  ollama pull mxbai-embed-large
  ```
  You can check available models and their details on the [Ollama model library](https://ollama.ai/library).

## Setting Up the Environment

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Python Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Requirements**

   Install the required Python packages using the `requirements.txt` file.

   ```bash
   pip install -r requirements.txt
   ```

## Setting Up PostgreSQL with Docker

1. **Create a Docker Network (Optional)**

   This step is optional but recommended for better organization.

   ```bash
   docker network create my_network
   ```

2. **Run PostgreSQL Using Docker Compose**

   Ensure your `docker-compose.yml` file is set up correctly. Then run:

   ```bash
   docker-compose up -d
   ```

   This command will start the PostgreSQL database in the background, with pgvector extension enabled and tables created.

   Table schema is defined in `init.sql` file, schema design is based on blog [thenile.building_code_assistant](https://thenile.dev/blog/building_code_assistant)

## Configuring Environment Variables

1. **Configure `.env` File for Docker**

   Create a file named `.env` in the project root and add the following configurations:

   ```env
   POSTGRES_DB=<your_database_name>
   POSTGRES_USER=<your_database_user>
   POSTGRES_PASSWORD=<your_database_password>
   POSTGRES_HOST_AUTH_METHOD=trust
   ```

   These variables will be used in the `docker-compose.yml` file to set up the PostgreSQL database.

2. **Configure `.env.chat` File**

   Configured `.env.chat` in the project root and add the following configurations:

   If you don't have a Gemini API key, you can use Ollama as the LLM. 

   ```env
   USE_OLLAMA=True
   GEMINI_API_KEY=<your_gemini_api_key>
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=<ollama_model_name>
   ```

3. **Create `.env.embed` File**

   Create a file named `.env.embed` in the project root and add the following configurations:

   Ensure you have the mxbai-embed-large model installed in your ollama server.

   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=mxbai-embed-large
   DB_CONNECTION_STRING=<DB_CONNECTION_STRING>
   ```

## Running the Application with Docker

1. **Build the Docker Image**

   To build the Docker image for the application, run:

   ```bash
   docker build -t code-assistant-ollama .
   ```

2. **Run the Docker Container**

   Start the application using Docker, exposing the necessary ports:

   ```bash
   docker run -p 8501:8501 -p 8502:8502 code-assistant-ollama
   ```

   This will run both the `chat.py` and `embeddings.py` applications, accessible at `http://localhost:8501` and `http://localhost:8502`, respectively.

## Running the Python Files

1. **Run the Chat App**

   To start the Streamlit application, run:

   ```bash
   streamlit run chat.py
   ```

2. **Run the Embeddings App**

   If you need to run the embeddings script, execute:

   ```bash
   streamlit run embeddings.py
   ```

## Stopping the Services

To stop the PostgreSQL service, run:
```bash
docker-compose down
```
