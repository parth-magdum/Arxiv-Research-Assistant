from graph_db import GraphDB

def get_graph(uri, user, password):
    return GraphDB(uri, user, password)

# load_dotenv()


# graph = GraphDB(
#     os.getenv("NEO4J_URI"),
#     os.getenv("NEO4J_USER"),
#     os.getenv("NEO4J_PASSWORD")
# )
