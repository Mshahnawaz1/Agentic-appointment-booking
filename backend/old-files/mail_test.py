import smtplib
from email.message import EmailMessage
import os 
from dotenv import load_dotenv
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")  
APP_PASSWORD = os.getenv("APP_PASSWORD")
# Sender details

# Create email
msg = EmailMessage()
msg["Subject"] = "TeAnAst Email from Python another test"
msg["From"] = EMAIL_ADDRESS
msg["To"] = "veldorano4@gmail.com"
msg.set_content("HeE! This is a test email sent using Gmail App Password.")

# Send email via Gmail SMTP
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(EMAIL_ADDRESS, APP_PASSWORD)
    smtp.send_message(msg)

print("Email sent successfully!")