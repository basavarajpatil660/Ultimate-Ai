import os
import requests
from agents.llm_agent import call_llm

def search_web(query):
    tavily_key = os.environ.get("TAVILY_API_KEY")
    jina_key = os.environ.get("JINA_API_KEY")
    
    results = []
    
    if tavily_key:
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "search_depth": "advanced", "include_raw_content": False},
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", [])[:5]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", "")
                    })
        except Exception as e:
            pass
            
    if not results and jina_key:
        # Fallback to Jina Reader if we had URLs but no content or search failed
        # Just stubbing this based on instructions since Tavily provides search
        pass
        
    return results

def research_and_synthesize(query):
    results = search_web(query)
    if not results:
        return {"provider": "search", "result": "No search results found."}
        
    context = ""
    for r in results:
        context += f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n\n"
        
    prompt = f"Based on the following search results, answer the query: '{query}'\n\nResults:\n{context}"
    llm_result = call_llm(prompt, "You are a helpful research assistant.")
    
    if llm_result:
        return llm_result
    return {"provider": "search", "result": "Failed to synthesize search results."}
