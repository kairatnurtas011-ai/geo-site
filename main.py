import chromadb
import json
import os


class GeoIndexer:
    def __init__(self):
        print("Запуск индексатора...")

        os.makedirs("./chroma_db", exist_ok=True)
        self.client = chromadb.PersistentClient(path="./chroma_db")


        self.collection = self.client.get_or_create_collection(
            name="geology_docs"
        )
        print("Индексатор готов!")

    def add_documents(self, chunks):
        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk["id"])
            texts.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        print(f"Добавлено {len(chunks)} фрагментов")

        self._build_graph(chunks)

    def _build_graph(self, chunks):
        graph = {}
        for chunk in chunks:
            text = chunk["text"].lower()
            entities = []
            if "скважина" in text or "well" in text:
                entities.append("well")
            if "пласт" in text or "formation" in text:
                entities.append("formation")
            if "нефтенасыщенность" in text:
                entities.append("parameter")

            if entities:
                graph[chunk["id"]] = {
                    "entities": entities,
                    "metadata": chunk["metadata"],
                    "text_preview": chunk["text"][:200]
                }

        with open("graph.json", "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)

        print(f"Построен граф с {len(graph)} узлами")

    def search(self, query: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results