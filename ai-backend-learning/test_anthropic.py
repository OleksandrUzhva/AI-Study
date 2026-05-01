import os
from dotenv import load_dotenv
import anthropic 


load_dotenv()
client_a = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")) 

message = client_a.messages.create( model="claude-haiku-4-5-20251001", # самый дешёвый 
    max_tokens=1024, system="Ты помощник разработчика", # отдельный параметр! 
    messages=[ {"role": "user", "content": "Что такое RAG?"} ] ) 
print(message.content[0].text)