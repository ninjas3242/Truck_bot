#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from src.utils.smart_search import search_knowledge
    print("Testing search...")
    results = search_knowledge("suggest me 5 trucks", max_results=5)
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"- {r.get('type', 'unknown')}: {r.get('title', 'no title')}")
except Exception as e:
    print(f"Search test error: {e}")
    import traceback
    traceback.print_exc()

try:
    from src.utils.ai_service import ai_service
    print("\nTesting AI service...")
    context = {'knowledge_base': {}}
    response = ai_service.generate_response("suggest me 5 trucks", context, "en")
    print(f"AI Response: {response[:200]}...")
except Exception as e:
    print(f"AI test error: {e}")
    import traceback
    traceback.print_exc()