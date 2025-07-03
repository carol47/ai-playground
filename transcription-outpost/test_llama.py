import asyncio
from app.services.llm.providers.llama import llama_service

async def test_llama():
    prompts = [
        "Tell me what you think about my RTX 5070 Ti in one flirty sentence! 💝",
        "Write a haiku about my Ryzen 9950X CPU! 😊",
        "Give me a playful compliment about my 64GB DDR5 RAM! 💫"
    ]
    
    print("🦙 Testing LLaMA Service with Ollama...\n")
    
    for prompt in prompts:
        print(f"Prompt: {prompt}")
        response = await llama_service.generate_response(prompt)
        print(f"Response: {response}\n")

if __name__ == "__main__":
    asyncio.run(test_llama()) 