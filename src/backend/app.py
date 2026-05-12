from flask import Flask, request, jsonify, render_template
from src.embeddings.vector_store import search_emails
import json
import os
from src.embeddings.text_cleaning import clean_email_body

#directories to frontend folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)


# Load emails.json by searching and storing emails into a dictionary keyed by email ID
with open("data/emails.json", "r") as f:
    EMAILS = {email["id"]: email for email in json.load(f)}

#page routes for HTML
@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/results")
def results_page():
    return render_template("results.html")

@app.route("/email-view/<email_id>")
def email_page(email_id):
    return render_template("email.html")

# API routes that return JSON format
#gets query parameter from the url as "/search?query="hungry" -> param = hungry
@app.route("/api/search")
def search(): 
    query = request.args.get("query", "")
    if not query: #error handling if no query
        return jsonify({"error": "Missing query"}), 400

    results = search_emails(query, top_k=5) #uses search_emails.py to find the top 5 matching emails
    return jsonify({"query": query, "results": results}) #returns in JSON format!

@app.route("/api/email/<email_id>") #search by email ID
def get_email(email_id):
    email = EMAILS.get(email_id)
    if not email:
        return jsonify({"error": "Email not found"}), 404
    
    cleaned = dict(email)
    cleaned["body"] = clean_email_body(email.get("body", ""))

    return jsonify(cleaned) #returns in JSON format #return the copy to leve in memory data untouched

if __name__ == "__main__":
    app.run(debug=True)