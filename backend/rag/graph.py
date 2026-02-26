import os
import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from rag.hybrid_search import hybrid_search
from rag.prompts import CONFLICT_DETECTION_PROMPT

class RAGState(TypedDict):
    query: str
    documents: List[dict]
    answer_json: dict

def retrieve_node(state: RAGState):
    query = state["query"]
    matches = hybrid_search(query, top_k=5)
    
    docs = []
    for m in matches:
        docs.append({
            "id": m["id"],
            "score": m["score"],  # RRF fused score
            "vector_score": m.get("vector_score", 0),
            "bm25_score": m.get("bm25_score", 0),
            "content": m["metadata"].get("text", ""),
            "metadata": m["metadata"]
        })
    return {"documents": docs}

def compute_confidence_breakdown(docs, llm_confidence):
    """
    Compute a weighted confidence score from real signals.
    
    Weights:
      - retrieval_similarity : 40%  (avg cosine similarity of top-K)
      - llm_confidence       : 30%  (DeepSeek self-assessed relevance)
      - source_diversity     : 15%  (unique departments / total docs)
      - score_spread         : 15%  (1 - normalized gap between top-1 and top-5)
    """
    scores = [d["score"] for d in docs] if docs else [0]
    
    # 1. Retrieval Similarity (0-100): avg of cosine sim scores
    avg_sim = sum(scores) / len(scores)
    retrieval_similarity = min(100, max(0, avg_sim * 100))
    
    # 2. LLM Confidence (0-100): from DeepSeek's self-assessment
    llm_conf = min(100, max(0, int(llm_confidence))) if llm_confidence else 50
    
    # 3. Source Diversity (0-100): unique departments / total docs
    departments = set()
    for d in docs:
        dept = d.get("metadata", {}).get("department", d.get("metadata", {}).get("filename", "unknown"))
        departments.add(dept)
    diversity_ratio = len(departments) / max(len(docs), 1)
    source_diversity = min(100, max(0, diversity_ratio * 100))
    
    # 4. Score Spread (0-100): inverted — tight cluster = high confidence
    if len(scores) >= 2:
        spread = scores[0] - scores[-1]  # gap between best and worst
        # A spread of 0 means all scores are the same (good), spread of 0.5+ is bad
        score_spread = min(100, max(0, (1 - spread * 2) * 100))
    else:
        score_spread = 50
    
    # Weighted final score
    weights = {
        "retrieval_similarity": 0.40,
        "llm_confidence": 0.30,
        "source_diversity": 0.15,
        "score_spread": 0.15,
    }
    
    final_score = (
        retrieval_similarity * weights["retrieval_similarity"]
        + llm_conf * weights["llm_confidence"]
        + source_diversity * weights["source_diversity"]
        + score_spread * weights["score_spread"]
    )
    
    final_score = min(100, max(0, round(final_score, 1)))
    
    # Determine label
    if final_score >= 70:
        label = "High"
    elif final_score >= 40:
        label = "Medium"
    else:
        label = "Low"
    
    return {
        "final_score": final_score,
        "label": label,
        "breakdown": {
            "retrieval_similarity": { "value": round(retrieval_similarity, 1), "weight": 40, "label": "Retrieval Similarity" },
            "llm_confidence":      { "value": round(llm_conf, 1),              "weight": 30, "label": "LLM Self-Confidence" },
            "source_diversity":    { "value": round(source_diversity, 1),       "weight": 15, "label": "Source Diversity" },
            "score_spread":        { "value": round(score_spread, 1),           "weight": 15, "label": "Score Consistency" },
        }
    }

def generate_node(state: RAGState):
    query = state["query"]
    docs = state["documents"]
    
    docs_text = ""
    for d in docs:
        # Exclude 'text' from metadata dump as it's printed as 'Content'
        meta_safe = {k: v for k,v in d["metadata"].items() if k != "text"}
        docs_text += f"---\nID: {d['id']}\nScore: {d['score']}\nMetadata: {json.dumps(meta_safe)}\nContent: {d['content']}\n"
        
    prompt = CONFLICT_DETECTION_PROMPT.format(query=query, documents=docs_text)
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is not set")

    llm = ChatOpenAI(
        model="deepseek-chat", 
        api_key=api_key, 
        base_url="https://api.deepseek.com",
        max_tokens=1024
    )
    
    response = llm.invoke(prompt)
    
    try:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        answer_data = json.loads(content)
    except Exception as e:
        answer_data = {
            "answer": "Failed to parse JSON response from LLM.",
            "conflicting_evidence": [],
            "confidence_level": "Low",
            "reasoning": f"Error: {str(e)}\nRaw Response: {response.content}",
            "llm_confidence": 20
        }
    
    # Extract DeepSeek's self-assessed confidence
    llm_conf = answer_data.pop("llm_confidence", 50)
    
    # Compute real weighted confidence
    confidence_data = compute_confidence_breakdown(docs, llm_conf)
    
    # Override the simple text label with computed data
    answer_data["confidence_level"] = confidence_data["label"]
    answer_data["confidence_score"] = confidence_data["final_score"]
    answer_data["confidence_breakdown"] = confidence_data["breakdown"]
    
    return {"answer_json": answer_data}

workflow = StateGraph(RAGState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate", generate_node)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app_graph = workflow.compile()

async def get_answer(query: str):
    final_state = app_graph.invoke({"query": query})
    result = final_state["answer_json"]
    result["provenance"] = final_state["documents"]
    return result
