from openai import OpenAI 
from dotenv import load_dotenv 
import os 
# import sys

load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

conversation = [{"role": "system", "content": "Ты помощник программиста"}] 
while True: 
    user_input = input("\nТы: ") 
    if user_input == "exit": 
        break 
    if user_input == "clear": 
        conversation = [conversation[0]] # оставляем только system 
        print("История очищена") 
        continue 

    conversation.append({"role": "user", "content": user_input}) 
    response = client.chat.completions.create( model="gpt-4o-mini", messages=conversation ) 
    reply = response.choices[0].message.content 
    conversation.append({"role": "assistant", "content": reply}) 
    print(f"\nGPT: {reply}")

