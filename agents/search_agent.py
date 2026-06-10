import os
import requests
from agents.llm_agent import call_llm

def scrape_with_jina(url, JINA_API_KEY):
    try:
        response = requests.get(
            f"https://r.jina.ai/{url}",
            headers={
                "Authorization": f"Bearer {JINA_API_KEY}",
                "Accept": "text/plain"
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.text[:3000]
    except Exception as e:
        print(f"Jina scrape failed: {e}")
    return None

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
                    content = item.get("content", "")
                    url = item.get("url", "")
                    if not content and jina_key and url:
                        content = scrape_with_jina(url, jina_key) or ""
                    results.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "content": content
                    })
        except Exception as e:
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
