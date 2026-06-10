import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def send_text(bot_token, chat_id, text):
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Split text into chunks of 4096 chars
    max_len = 4096
    chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
    
    for chunk in chunks:
        data = {"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"}
        requests.post(url, json=data)

def send_image(bot_token, chat_id, image_path, caption):
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    caption = caption[:1024]
    
    with open(image_path, 'rb') as f:
        files = {"photo": f}
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        requests.post(url, data=data, files=files)

def send_audio(bot_token, chat_id, audio_path, caption):
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    caption = caption[:1024]
    
    with open(audio_path, 'rb') as f:
        files = {"audio": f}
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        requests.post(url, data=data, files=files)

def send_alert(bot_token, chat_id, message):
    alert_text = f"⚠️ {message}"
    send_text(bot_token, chat_id, alert_text)

def send_email(gmail_address, app_password, to_address, subject, body):
    if not gmail_address or not app_password or not to_address:
        return
        
    msg = MIMEMultipart()
    msg['From'] = gmail_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_address, app_password)
        text = msg.as_string()
        server.sendmail(gmail_address, to_address, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
