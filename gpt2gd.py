import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

# Set up OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# OAuth 2.0 scopes and credentials management
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Load or refresh credentials
def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Upload file to Google Drive
def upload_to_drive(creds, content, file_name):
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_name, mimetype='text/plain')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

# Generate GPT chat and save to Google Drive
def save_chat_to_drive():
    prompt = "Explain the importance of cloud computing in modern businesses."
    response = openai.Completion.create(
        model="text-davinci-004",
        prompt=prompt,
        max_tokens=150
    )
    chat_transcript = response.choices[0].text.strip()
    
    # Securely create and upload the transcript
    file_name = "GPT_Chat_Transcript.txt"
    with open(file_name, 'w') as f:
        f.write(chat_transcript)
    
    # Upload to Google Drive
    creds = get_credentials()
    upload_to_drive(creds, chat_transcript, file_name)
    
    # Clean up
    os.remove(file_name)

if __name__ == "__main__":
    save_chat_to_drive()
