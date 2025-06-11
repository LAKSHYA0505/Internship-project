import os
from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Retrieve Azure credentials from environment variables
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

if not AZURE_LANGUAGE_KEY or not AZURE_LANGUAGE_ENDPOINT:
    raise ValueError("Azure Language Key or Endpoint not found in environment variables. Please check your .env file.")

# Authenticate the Text Analytics client
text_analytics_client = TextAnalyticsClient(
    endpoint=AZURE_LANGUAGE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_LANGUAGE_KEY)
)

@app.route('/')
def index():
    return "Welcome to the HMS Feedback Backend!"

@app.route('/analyze-feedback', methods=['POST'])
def analyze_feedback():
    data = request.get_json()
    if not data or 'feedback_text' not in data:
        return jsonify({"error": "Invalid request. 'feedback_text' is required."}), 400

    feedback_text = data['feedback_text']
    print(f"Received feedback: '{feedback_text}'")

    try:
        # Perform sentiment analysis
        sentiment_response = text_analytics_client.analyze_sentiment(
            documents=[feedback_text],
            show_opinion_mining=False
        )
        sentiment_result = sentiment_response[0]

        sentiment = sentiment_result.sentiment
        confidence_scores = {
            "positive": sentiment_result.confidence_scores.positive,
            "neutral": sentiment_result.confidence_scores.neutral,
            "negative": sentiment_result.confidence_scores.negative,
        }

        # Perform key phrase extraction
        key_phrase_response = text_analytics_client.extract_key_phrases(
            documents=[feedback_text]
        )
        key_phrases = key_phrase_response[0].key_phrases if key_phrase_response[0].key_phrases else []


        return jsonify({
            "sentiment": sentiment,
            "confidence_scores": confidence_scores,
            "key_phrases": key_phrases
        })

    except Exception as e:
        print(f"Error processing feedback: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)