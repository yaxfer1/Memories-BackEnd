import os
from dotenv import load_dotenv
from getpass import getpass
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm
import dbManagement
import re

load_dotenv()

def normalize_vector_id(file_name):
    # Remueve caracteres no alfanuméricos, convierte a minúsculas y reemplaza espacios con guiones bajos
    return re.sub(r'[^a-zA-Z0-9_-]', '', file_name.replace(' ', '_')).lower()

pcapi_key = os.getenv('PINECONE2_API_KEY')

# Configurar Pinecone
pc = Pinecone(api_key=pcapi_key)
spec = ServerlessSpec(cloud="aws", region="us-east-1")

# Nombre del índice de Pinecone
index_name = "prueba-leyton"
index = pc.Index(index_name)

# Modelo de embeddings
embed = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))

# Clase para procesar PDFs y guardar embeddings
class PDFProcessor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size

    def extract_text_from_pdf(self, file):
        """
        Extrae texto de un archivo PDF.
        """
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        return text

    def split_text(self, text, chunk_size=1000):
        """
        Divide el texto en fragmentos de tamaño fijo.
        """
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    def process_pdfs_and_insert(self, pdf_files, memory_id):
        """
        Procesa múltiples archivos PDF, genera embeddings y los guarda en Pinecone.
        """
        for pdf_file in tqdm(pdf_files):
            # Extraer texto del PDF
            text = self.extract_text_from_pdf(pdf_file)

            if not text.strip():
                print(f"El archivo {pdf_file.filename} está vacío o no tiene texto extraíble.")
                continue
            dbManagement.add_new_pdf(pdf_file.filename, text, memory_id)
            # Dividir texto en fragmentos
            chunks = self.split_text(text)
            print("chunks:")
            print(chunks)

            # Procesar por lotes
            for i in range(0, len(chunks), self.batch_size):
                batch_chunks = chunks[i:i + self.batch_size]
                print("batch_chunks")
                print(batch_chunks)

                # Generar IDs únicos para cada chunk del lote
                ids = [
                    normalize_vector_id(f"{pdf_file.filename}-{i + idx}")
                    for idx in range(len(batch_chunks))
                ]

                # Generar embeddings para el lote
                embeds = embed.embed_documents(batch_chunks)

                # Crear metadatos
                metadata = [{'text': chunk, 'source': pdf_file.filename} for chunk in batch_chunks]

                # Subir a Pinecone
                vectors = list(zip(ids, embeds, metadata))
                index.upsert(vectors=vectors)

        print(f"Procesado y subido el archivo {pdf_file.filename} a Pinecone.")

class URLProcessor:
    def __init__(self):
        pass

    def process_text(self, text, url):
        """
        Procesa el texto completo de una URL, genera embeddings y los guarda en Pinecone.
        """
        if not text.strip():
            print(f"El texto de la URL {url} está vacío o no es procesable.")
            return

        # Asegúrate de que la URL sea una cadena (decodifica si es bytes)
        vector_id = url.decode('utf-8') if isinstance(url, bytes) else url
        print(vector_id)
        # Generar el embedding para el texto completo
        embed_vector = embed.embed_query(text)

        # Crear metadatos para el texto completo
        metadata = {'text': text, 'source': vector_id}

        # Subir el vector a Pinecone
        index.upsert(vectors=[(vector_id, embed_vector, metadata)])

        print(f"Procesado y subido el contenido completo de {vector_id} a Pinecone.")
