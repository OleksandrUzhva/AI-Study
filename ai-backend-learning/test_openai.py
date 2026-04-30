from openai import OpenAI 
from dotenv import load_dotenv 
import os 

load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
response = client.chat.completions.create( model="gpt-4o-mini", 
messages=[ 
    {"role": "system", "content": "Ты помощник разработчика. Отвечай кратко."}, 
    {"role": "user", "content": "Меня зовут Олександр"},
    {"role": "assistant", "content": "Привет, Олександр! Чем могу помочь?"},
    {"role": "user", "content": "Ты помнишь как меня зовут?"}
    ], temperature=0.7, max_tokens=200 ) 
print(response.choices[0].message.content) 
print(f"Токенов использовано: {response.usage.total_tokens}")