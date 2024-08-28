import time  # Add this import at the top of the file
import streamlit as st
import os
import uuid
import psycopg2
from psycopg2.extras import execute_values
from langchain.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from dotenv import load_dotenv

# Load environment variables from .env.embed file
load_dotenv(dotenv_path='.env.embed')

# Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL')
DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings(
  base_url=OLLAMA_BASE_URL,
  model=OLLAMA_MODEL
)

tenant_id = "2fb5d43b-266a-4eef-89a8-8ca495dd9f06"
project_id = "3e34e3d2-e840-42de-b96b-e75c0ac986de"

def create_connection():
  return psycopg2.connect(DB_CONNECTION_STRING)

def insert_file_content(conn, tenant_id, project_id, file_name, contents):
  with conn.cursor() as cur:
      cur.execute("""
          INSERT INTO file_content (tenant_id, project_id, file_name, contents)
          VALUES (%s, %s, %s, %s)
          RETURNING id
      """, (tenant_id, project_id, file_name, contents))
      return cur.fetchone()[0]

def insert_embeddings(conn, tenant_id, file_id, embedding):
  with conn.cursor() as cur:
      cur.execute("""
          INSERT INTO embeddings_mxbai_text (tenant_id, file_id, embedding)
          VALUES (%s, %s, %s)
      """, (tenant_id, file_id, embedding))

def process_file(file_path, tenant_id, project_id):
  loader = TextLoader(file_path)
  documents = loader.load()
  
  for doc in documents:
      file_name = os.path.basename(file_path)
      contents = doc.page_content
      
      with create_connection() as conn:
          file_id = insert_file_content(conn, tenant_id, project_id, file_name, contents)
          
          # Generate embedding
          embedding = embeddings.embed_query(contents)
          
          insert_embeddings(conn, tenant_id, file_id, embedding)
          conn.commit()

def process_folder(folder_path, tenant_id, project_id):
  loader = DirectoryLoader(folder_path, glob="**/*.txt")
  documents = loader.load()
  
  for doc in documents:
      file_name = os.path.basename(doc.metadata['source'])
      contents = doc.page_content
      
      with create_connection() as conn:
          file_id = insert_file_content(conn, tenant_id, project_id, file_name, contents)
          
          # Generate embedding
          embedding = embeddings.embed_query(contents)
          
          insert_embeddings(conn, tenant_id, file_id, embedding)
          conn.commit()

def main():
    st.title("File Embeddings Generator")

    # Add input fields for tenant ID and project ID
    #tenant_id = st.text_input("Tenant ID", value=str(uuid.uuid4()), help="Enter the tenant ID or leave blank for a new UUID")
    #project_id = st.text_input("Project ID", value=str(uuid.uuid4()), help="Enter the project ID or leave blank for a new UUID")

    # Display the entered or generated IDs
    st.write(f"Tenant ID: {tenant_id}")
    st.write(f"Project ID: {project_id}")

    upload_type = st.radio("Choose upload type:", ("File", "Folder"))

    if upload_type == "File":
        handle_file_upload(tenant_id, project_id)
    else:
        handle_folder_processing(tenant_id, project_id)

    st.write("Note: This app processes .txt files only.")

def handle_file_upload(tenant_id, project_id):
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "java", "py"])
    if uploaded_file is not None:
        with st.spinner("Processing file..."):
            start_time = time.time()  # Start the timer
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            process_file(uploaded_file.name, tenant_id, project_id)
            
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            
            # Remove the temporary file
            os.remove(uploaded_file.name)
        
        st.success(f"File processed successfully in {elapsed_time:.2f} seconds!")  # Display elapsed time

def handle_folder_processing(tenant_id, project_id):
    folder_path = st.text_input("Enter folder path:")
    if st.button("Process Folder"):
        if os.path.isdir(folder_path):
            with st.spinner("Processing folder..."):
                process_folder(folder_path, tenant_id, project_id)
            st.success("Folder processed successfully!")
        else:
            st.error("Invalid folder path. Please enter a valid directory path.")

if __name__ == "__main__":
    main()