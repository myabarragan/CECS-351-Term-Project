# this program fectches emails from a user's gmail account and returns the content as a json file

import base64, json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os, pickle

# defines read only access in to a user's gmail account
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    '''
    This function builds a Gmail API client using a user's authenticated credentials
    '''
    creds = None        # start with no saved credentials
    
    # if a user has signed in before, load their token file
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        # if user credentials are expired, refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # if the user hasn't created credentials, have them log in and grant access
        else:
            flow = InstalledAppFlow.from_client_secrets_file('data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def fetch_message_ids(service, max_count=2000):
    ''' fetch up to max_count message IDs'''
    message_ids = []
    page_token = None

    while len(message_ids) < max_count:
        response = service.users().messages().list(
            userId='me',
            maxResults=500,
            pageToken=page_token
        ).execute()

        batch = response.get('messages', [])
        message_ids.extend(batch)

        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return message_ids[:max_count]

def extract_header(headers, name):
    '''Helper function to extract header value'''
    return next((h['value'] for h in headers if h['name'] == name), '')

def get_body(payload):
    """Extract the body from a Gmail message payload, handling multipart emails."""
    
    # Simple email with body in payload['body']['data']
    if 'data' in payload.get('body', {}):
        data = payload['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    # Multipart email — recursively search parts
    parts = payload.get('parts', [])
    for part in parts:
        # Prefer plain text
        if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
            data = part['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    # If no plain text, try HTML
    for part in parts:
        if part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
            data = part['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

    # Deeply nested parts — recurse
    for part in parts:
        nested = get_body(part)
        if nested:
            return nested

    return ""


service = get_service()
message_ids = fetch_message_ids(service, max_count=2000)

# store the email content (ID, subject, body, )
emails = []

for msg in message_ids:
    m = service.users().messages().get(
        userId='me',
        id=msg['id'],
        format='full'
    ).execute()

    headers = m['payload']['headers']

    subject = extract_header(headers, 'Subject')
    sender = extract_header(headers, 'From')
    date_str = extract_header(headers, 'Date')
    body = get_body(m['payload'])

    emails.append({
        "id": msg['id'],
        "subject": subject,
        "sender": sender,
        "date": date_str,
        "body": body
    })   

# save content to emails.json
with open('data/emails.json', 'w') as f:
    json.dump(emails, f, indent=2)

print("Saved emails.json with", len(emails), "emails")
