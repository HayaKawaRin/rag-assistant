# import json
# from pathlib import Path
# from sqlalchemy.orm import Session

# from app.services.retrieval.retrieval_orchestrator import retrieve_context
# from app.services.generation.prompt_service import build_answer_prompt
# from app.services.generation.generation_service import generate_answer


# def load_dataset(path: str = "app/evaluation/dataset.json") -> list[dict]:
#     return json.loads(Path(path).read_text(encoding="utf-8"))


# def evaluate_rag(db: Session, dataset_path: str = "app/evaluation/dataset.json") -> list[dict]:
#     dataset = load_dataset(dataset_path)
#     results = []

#     for item in dataset:
#         question = item["question"]
#         expected_keywords = [kw.lower() for kw in item.get("expected_keywords", [])]
#         expected_source = item.get("expected_source_filename")

#         retrieval_data = retrieve_context(db, question)
#         prompt = build_answer_prompt(question, retrieval_data["context_preview"])
#         answer = generate_answer(prompt)

#         answer_lc = answer.lower()
#         found_keywords = [kw for kw in expected_keywords if kw in answer_lc]
#         source_filenames = [src["filename"] for src in retrieval_data["sources"]]

#         results.append(
#             {
#                 "question": question,
#                 "expected_source": expected_source,
#                 "retrieved_sources": source_filenames,
#                 "source_hit": expected_source in source_filenames if expected_source else None,
#                 "keyword_hits": found_keywords,
#                 "keyword_recall": round(
#                     len(found_keywords) / len(expected_keywords), 3
#                 ) if expected_keywords else None,
#                 "answer": answer,
#             }
#         )

#     return results