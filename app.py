from flask import Flask, render_template, request, url_for
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import requests

url = "https://google-translate113.p.rapidapi.com/api/v1/translator/text"

rapid_key = os.getenv('RAPID_API_KEY')  
headers = {
	"x-rapidapi-host": "google-translate113.p.rapidapi.com",
    "x-rapidapi-key": rapid_key,
	"Content-Type": "application/json"
}


app = Flask(__name__)
load_dotenv('key.env')
key = os.getenv('API_KEY')

def split_text(text, max_length=500):
    # Splits text into chunks of max_length, trying to split at line breaks
    lines = text.split('\n')
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks

@app.route('/retrieve_summary', methods=['POST'])
def get_summary():
    client = genai.Client(api_key=key)
    url_input = request.form['policyLink']
    language_code = request.form['language']  # Get the selected language code

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="""You are a helpful assistant whose primary task is to analyze and summarize the privacy policy 
            text provided to you. Your response should be structured into three clear sections: 
            a concise overview under 'Summary,' 
            specific elements users should be cautious about under 'Points of Concern,' 
            and a categorization of key points labeled as Good, Neutral, or Bad. 
            Do not include any introductory or concluding phrases, restate the policy name or prompt, 
            or use creative tone or formatting. Your output must strictly follow this structure and 
            avoid any text that is not part of the analysis itself.""",
        ),
        contents=url_input
    )

    # Split the summary into chunks
    max_chars = 500  # Adjust based on API docs
    chunks = split_text(response.text, max_chars)
    translated_chunks = []
    for chunk in chunks:
        payload = {
            "from": "en",
            "to": language_code,
            "text": chunk
        }
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            translated_chunks.append(resp.json().get('trans', ''))
        else:
            translated_chunks.append('[Translation failed]')
    translated_text = "\n".join(translated_chunks)
    return render_template('summary.html', summary=translated_text)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)