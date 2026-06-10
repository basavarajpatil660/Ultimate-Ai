from agents.llm_agent import call_llm

def generate_content(prompt):
    system_prompt = """You are an expert content creator and strategist.
Your task is to generate highly engaging, well-structured content based on the user's prompt.
If the prompt is about YouTube or gaming, tailor it specifically for high retention and engagement."""
    
    result = call_llm(prompt, system_prompt=system_prompt)
    return result
