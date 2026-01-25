


import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pydantic import BaseModel, EmailStr, Field

from db.schemas import Tool_response
from app import app


