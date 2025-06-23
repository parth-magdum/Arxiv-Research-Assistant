from graph_db import GraphDB
from dotenv import load_dotenv
import os

load_dotenv()

# print("Loaded from .env:")
# print("URI:", os.getenv("NEO4J_URI"))
# print("USER:", os.getenv("NEO4J_USER"))
# print("PASS (partial):", os.getenv("NEO4J_PASSWORD")[:6], "...")

graph = GraphDB(
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD")
)
