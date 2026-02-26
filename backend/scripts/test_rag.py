import asyncio
import os
from dotenv import load_dotenv

# Ensure dotenv is loaded before imports that might need it
load_dotenv()

from rag.graph import get_answer

async def test_conflict():
    query = "How has patient satisfaction changed over Q1?"
    print(f"Testing Query: {query}")
    result = await get_answer(query)
    
    print("\n--- RESULT ---")
    print(f"Answer: {result.get('answer')}")
    print(f"Confidence Level: {result.get('confidence_level')}")
    print("Conflicting Evidence:")
    for ce in result.get('conflicting_evidence', []):
        print(f" - {ce}")
    print(f"Reasoning: {result.get('reasoning')}")
    
    print("\n--- PROVENANCE ---")
    for doc in result.get('provenance', []):
        print(f"[{doc['id']}] Score: {doc['score']:.4f}")

if __name__ == "__main__":
    asyncio.run(test_conflict())
