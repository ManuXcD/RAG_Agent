import os
from dotenv import load_dotenv
import requests

import imaplib
import email
import email.header
import smtplib


# Load environment variables from .env file
load_dotenv()

BASE_API_URL = os.getenv("BASE_API_URL")
FLOW_ID = os.getenv("FLOW_ID")
ENDPOINT = os.getenv("ENDPOINT")
APPLICATION_TOKEN = os.getenv("APP_KEY")

# Connect to Email Server and Read Emails
def read_emails(email_user, email_pass):
    
    # connect to host using SSL
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    
    ## login to server
    mail.login(email_user, email_pass)
    
    mail.select("Inbox")
    
    status, messages = mail.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    
    latest_email_id = email_ids[-1]
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    
    msg = email.message_from_bytes(msg_data[0][1])
    
    return msg

# this function decode mime words
def decode_mime_words(header):
    decoded_parts = email.header.decode_header(header)
    result = ''.join(part.decode(encoding or 'utf-8', errors='replace') if isinstance(part, bytes) else str(part)
        for part, encoding in decoded_parts)
    return result

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

# Search Knowledge Base
def search_knowledge_base(email_subject: str, customer_email: str, email_content: str)-> dict:
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
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_user, email_pass)

    message = f"Subject: Re: {email_subject}\n\n{reply}"
    
    server.sendmail(email_user, to_address, message)
    
    server.quit()


# Main Function
def main():
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASS = os.getenv('EMAIL_PASS')
    
    emailContent = read_emails(EMAIL_USER, EMAIL_PASS)
    
    email_subject, customer_email, email_content = extract_email_data(emailContent)

    ai_response = search_knowledge_base(email_subject, customer_email, email_content)

    # reply = prepare_reply(ai_response)

    # print(ai_response)
       
    # reply_message = prepare_reply(searchResult)
    
    send_reply(EMAIL_USER, EMAIL_PASS, customer_email, email_subject, ai_response )

if __name__ == "__main__":
    main()