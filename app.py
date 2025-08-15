from flask import Flask, render_template, request, url_for
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv('key.env')
key = os.getenv('API_KEY')
@app.route('/retrieve_summary', methods=['POST'])
def get_summary():
    client = genai.Client(api_key=key)
    url = request.form['policyLink']
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

        contents=url
    )
    return render_template('summary.html', summary=response.text)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)