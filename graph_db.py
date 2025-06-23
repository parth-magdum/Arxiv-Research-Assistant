from neo4j import GraphDatabase

class GraphDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))


    def close(self):
        self.driver.close()

    def add_paper(self, title, url, authors, topic):
        with self.driver.session() as session:
            session.execute_write(self._create_graph, title, url, authors, topic)

    @staticmethod
    def _create_graph(tx, title, url, authors, topic):
        tx.run("""
            MERGE (t:Topic {name: $topic})
            MERGE (p:Paper {title: $title, url: $url})
            MERGE (p)-[:BELONGS_TO]->(t)
            WITH p
            UNWIND $authors AS author
            MERGE (a:Author {name: author})
            MERGE (a)-[:WROTE]->(p)
        """, title=title, url=url, authors=authors, topic=topic)

        
    def get_papers_by_author(self, author_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Author {name: $name})-[:WROTE]->(p:Paper)
                RETURN p.title AS title, p.url AS url
            """, name=author_name)
            return result.data()