import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyAz-k9n9sthDL74W_jN1fWcqfPKM4Us8rI")

print("Available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error:", e)
