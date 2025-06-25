from graph_db import GraphDB
from dotenv import load_dotenv
import os

load_dotenv()


graph = GraphDB(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
)
