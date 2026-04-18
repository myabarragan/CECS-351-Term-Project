from flask import Flask, request, jsonify
from src.embeddings.vector_store import search_emails
import json

app = Flask(__name__)

# Load emails.json by searching and storing emails into a dictionary keyed by email ID
with open("data/emails.json", "r") as f:
    EMAILS = {email["id"]: email for email in json.load(f)}

#gets query parameter from the url as "/search?query="hungry" -> param = hungry
@app.route("/search")
def search(): 
    query = request.args.get("query", "")
    if not query: #error handling if no query
        return jsonify({"error": "Missing query"}), 400

    results = search_emails(query, top_k=5) #uses search_emails.py to find the top 5 matching emails
    return jsonify(results) #returns in JSON format!

@app.route("/email/<email_id>") #search by email ID
def get_email(email_id):
    email = EMAILS.get(email_id)
    if not email:
        return jsonify({"error": "Email not found"}), 404

    return jsonify(email) #returns in JSON format

if __name__ == "__main__":
    app.run(debug=True)