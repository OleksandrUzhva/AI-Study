from openai import OpenAI 
from dotenv import load_dotenv 
import os 
#import sys

load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

#response = client.chat.completions.create( model="gpt-4o-mini", 
#messages=[ 
    #{"role": "system", "content": "Ты помощник разработчика. Отвечай кратко."}, 
    #{"role": "user", "content": "Меня зовут Олександр"},
    #{"role": "assistant", "content": "Привет, Олександр! Чем могу помочь?"},
    #{"role": "user", "content": "Ты помнишь как меня зовут?"}
    #], temperature=0.7, max_tokens=500 ) 
#print(response.choices[0].message.content) 
#print(f"Токенов использовано: {response.usage.total_tokens}")


#stream = client.chat.completions.create( model="gpt-4o-mini",
#messages=[
    #{"role": "user", "content": "Расскажи о Python за 50 слов"}
    #], stream=True ) 
#full_response = "" 
#for chunk in stream: 
    #delta = chunk.choices[0].delta.content 
    #if delta: 
        #print(delta, end="", flush=True) 
        #full_response += delta 
#print(f"\nВсего символов: {len(full_response)}")


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