import os
from dotenv import load_dotenv
import requests
import imaplib
import email
import email.header
import smtplib
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Load environment variables from .env file
load_dotenv()

BASE_API_URL = os.getenv("BASE_API_URL")
FLOW_ID = os.getenv("FLOW_ID")
ENDPOINT = os.getenv("ENDPOINT")
APPLICATION_TOKEN = os.getenv("APP_KEY")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
CHECK_INTERVAL = 60  # Check inbox every 60 seconds

# Connect to Email Server and Read Emails
def get_unread_emails(email_user, email_pass):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER) # connect to host using SSL
    mail.login(email_user, email_pass) # login to server
    mail.select("Inbox")

    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    email_data = []

    for e_id in email_ids:
        result, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_subject, customer_email, email_content = extract_email_data(msg)
                email_data.append({"id": e_id.decode(), "sender": customer_email,"subject":email_subject, "body": email_content})
                
    mail.logout()
    return email_data

# Extract Data from Email
def extract_email_data(msg):
    subject = decode_mime_words(msg["Subject"])
    from_ = decode_mime_words(msg["From"])
    
    if msg.is_multipart():
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()
        
    return subject, from_, body

# this function decode mime words
def decode_mime_words(header):
    decoded_parts = email.header.decode_header(header)
    result = ''.join(part.decode(encoding or 'utf-8', errors='replace') if isinstance(part, bytes) else str(part)
        for part, encoding in decoded_parts)
    return result

# Search Knowledge Base
def search_knowledge_base(email_content: str)-> dict:
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"

    # payload = {
    # "email_subject": email_subject,
    # "customer_email": customer_email,
    # "email_content": email_content,
    # "expected_reply_format": "Provide a structured response including:\n- A polite greeting\n- A brief overview of Mediclaim insurance\n- Coverage details\n- Premium cost (if applicable)\n- Key benefits\n- A call to action (e.g., contact for more details)\n- A professional tone",
    # "output_type": "text",
    # "input_type": "text",
    # }

    payload = {
        "input_value": email_content,
        "output_type": "chat",
        "input_type": "chat",
    }
    
    headers = {"x-api-key": APPLICATION_TOKEN}
    response = requests.post(api_url, json=payload, headers=headers)
    response = response.json()
    response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    return response


#Send Reply via Email
def send_reply(email_user, email_pass, to_address, email_subject, reply):
    server = smtplib.SMTP(SMTP_SERVER, 587)
    server.starttls()
    server.login(email_user, email_pass)

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["Subject"] = f"Re: {email_subject}"

    msg.attach(MIMEText(reply, "plain"))

    server.sendmail(email_user, to_address, msg.as_string())
    
    server.quit()


# Main Function
def main():
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASS = os.getenv('EMAIL_PASS')
    
    while True:
        print("Processing new unread emails...")
        unread_emails = get_unread_emails(EMAIL_USER, EMAIL_PASS)
        for email in unread_emails:
            print("Awaiting for response from AI Email Assistant...")
            ai_response = search_knowledge_base(email['body'])
            send_reply(EMAIL_USER, EMAIL_PASS, email['sender'], email['subject'], ai_response)
       
        print("All new emails have been processed and replied.")
        print("Waiting for next check...")
        time.sleep(CHECK_INTERVAL)  # Wait before checking again

if __name__ == "__main__":
    main()