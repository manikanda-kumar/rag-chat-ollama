import streamlit as st
from google.generativeai import GenerativeModel, configure
import google.generativeai as genai
from langchain_community.chat_models import ChatOllama
import psycopg2
from sqlalchemy import create_engine
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import uuid
from psycopg2.extras import execute_values
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from dotenv import load_dotenv

# Load environment variables from .env.chat file
load_dotenv(dotenv_path='.env.chat')

# Configuration
USE_OLLAMA = os.getenv("USE_OLLAMA", "False") == "True"  # Convert to boolean
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Replace with your actual Gemini API key
# OLLAMA Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")  # Default if not set
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "mxbai-embed-large")

# Configure the Gemini API
configure(api_key=GEMINI_API_KEY)

# Input for project ID
project_id = "3e34e3d2-e840-42de-b96b-e75c0ac986de"  

# Initialize the model based on the flag
if USE_OLLAMA:
    model = ChatOllama(model=OLLAMA_MODEL)
else:
    model = GenerativeModel('gemini-pro')

# Database connection parameters
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))
DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings(
  base_url=OLLAMA_BASE_URL,
  model=EMBEDDINGS_MODEL
)

# Initialize Ollama LLM
ollama_llm = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)

def connect_to_db():
  try:
      conn = psycopg2.connect(
          dbname=DB_NAME,
          user=DB_USER,
          password=DB_PASSWORD,
          host=DB_HOST,
          port=DB_PORT
      )
      return conn
  except psycopg2.Error as e:
      print(f"Error connecting to the database: {e}")
      return None

def get_embeddings_v3(project_id, query_embedding):
   conn = connect_to_db()
   cursor = conn.cursor()
   embedding_res=""
   query = """    
    SELECT file_id, file_name, contents, (embedding <=> %s::vector) as similarity
    FROM embeddings_mxbai_text
    JOIN file_content fc ON fc.id = file_id
    WHERE fc.project_id = %s
    ORDER BY similarity
    LIMIT 1    
   """
   try:
    cursor.execute(query, (query_embedding, project_id))
    embedding_res = cursor.fetchall()
   except Exception as e:
      print("Error in get_embeddings_v3", e)
      raise e
   finally:
      conn.close()
   return embedding_res

def generate_response(context, user_query, model, USE_OLLAMA):
    # Create the prompt
    prompt = f"Context:\n{context}\n\nQuestion: {user_query}\n\nAnswer:"

    # Generate response based on the selected model
    if USE_OLLAMA:
        response = model.invoke(prompt)
        answer = response.content
    else:
        response = model.generate_content(prompt)
        answer = response.text

    return answer

def main():
  st.title("Langchain Ollama Chatbot")

  # Input for user query
  user_query = st.text_input("Enter your question:")
  answer= "No Answer"

  if st.button("Get Answer"):
      if user_query:
          # Generate embedding for the user query
          query_embedding = embeddings.embed_query(user_query)
          #print("query_embedding", query_embedding)
                   
          try:
              relevant_embeddings = get_embeddings_v3(project_id, query_embedding)              

              if not relevant_embeddings:
                  st.write("No relevant information found.")
              else:
                  # Prepare context from retrieved embeddings
                  context = "\n".join([f"File: {e[1]}\nContent: {e[2]}" for e in relevant_embeddings])
                  print("Relevant file names:")
                  for e in relevant_embeddings:
                      print(f"- {e[1]}")                        
                
                  print("Context to be passed to LLM: ")
                  print(context)
                  # Generate and display the response
                  answer = generate_response(context, user_query, model, USE_OLLAMA)
                  st.write("Answer:", answer)
          except Exception as e:
              st.write(f"An error occurred: {str(e)}")
              # Optionally, you can log the error or handle it in a specific way
              # logging.error(f"Error in processing query: {str(e)}")

if __name__ == "__main__":
  main()