from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, documents):
        self.docs = documents
        self.texts = [doc.page_content for doc in documents]

        if not self.texts:
            self.bm25 = None
            return

        tokenized_docs = [text.split() for text in self.texts]
        self.bm25 = BM25Okapi(tokenized_docs)

    def search_with_scores(self, query):
        if not self.bm25:
            return []

        tokenized_query = query.split()
        scores = self.bm25.get_scores(tokenized_query)

        return list(zip(self.docs, scores))


def hybrid_retrieval(query, vector_db, bm25_retriever, use_web=False):

    combined_results = {}

    # VECTOR SEARCH (FIXED)
    
    try:
        vector_results = vector_db.similarity_search_with_score(query, k=5)

        for doc, score in vector_results:
            content = doc.page_content
            meta = doc.metadata or {}

            sim_score = 1 / (1 + score)

            combined_results[content] = {
                "content": content,
                "vector_score": sim_score,
                "bm25_score": 0,
                "source": meta.get("source", "document"),
                "chunk_id": meta.get("chunk_id", "?"),
                "page": meta.get("page", "?"),
                "is_image": meta.get("is_image", False)
            }

    except Exception as e:
        print("Vector error:", e)

   
    # BM25 SEARCH
    
    try:
        if bm25_retriever and bm25_retriever.bm25:
            bm25_results = bm25_retriever.search_with_scores(query)

            for doc, score in bm25_results:
                content = doc.page_content

                if content in combined_results:
                    combined_results[content]["bm25_score"] = score
                else:
                    combined_results[content] = {
                        "content": content,
                        "vector_score": 0,
                        "bm25_score": score,
                        "source": "bm25",
                        "chunk_id": "?",
                        "page": "?",
                        "is_image": False
                    }

    except Exception as e:
        print("BM25 error:", e)

    
    # NORMALIZE BM25

    max_bm25 = max([v["bm25_score"] for v in combined_results.values()], default=1)

    for v in combined_results.values():
        v["bm25_score"] = v["bm25_score"] / max_bm25 if max_bm25 else 0

   
    # FINAL SCORE
    
    for v in combined_results.values():
        v["final_score"] = 0.7 * v["vector_score"] + 0.3 * v["bm25_score"]

   
    # SORT
    
    sorted_results = sorted(
        combined_results.values(),
        key=lambda x: x["final_score"],
        reverse=True
    )

    top_results = sorted_results[:5]

    return top_results