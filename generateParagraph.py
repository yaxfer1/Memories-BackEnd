import os
import logging
logging.basicConfig(level=logging.INFO)
from semantic_router.encoders import OpenAIEncoder
from langchain.globals import set_verbose

set_verbose(True)
encoder = OpenAIEncoder(name="text-embedding-3-small")
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=10000,
    api_key=os.getenv("OPENAI_API_KEY")
)

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

system_prompt = """
Eres un asistente especializado en la redacción de reportes y memorias técnicas para proyectos empresariales.

Se te proporcionará un texto estructurado en el siguiente orden:

- Párrafo base: Fragmento inicial del apartado que se debe desarrollar o ampliar.
- Contexto adicional: Información relevante extraída mediante herramientas de LangChain, que puede incluir datos específicos, resultados de análisis o detalles sobre las herramientas utilizadas.
- Instrucciones específicas: Directrices adicionales que debes seguir durante la generación del contenido.
Tu objetivo es desarrollar apartados técnicos claros, coherentes y detallados, adaptados a los estándares de documentación empresarial. El contenido debe ser formal, preciso y alineado con el contexto proporcionado, contribuyendo a la construcción de reportes profesionales y de alta calidad.
"""


prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}"),
])
generacion = prompt | llm



def generateParagraph(input):
    print("input de generacion: ")
    print(input)
    generatedpar = generacion.invoke(input=input)
    print(generatedpar)
    return generatedpar.content