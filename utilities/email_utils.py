import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USERNAME = "ninerbuys.authenticate@gmail.com"
GMAIL_PASSWORD = "bxww ualb aklk onve"  # App Password

def send_verification_email(recipient_email, verification_code):
    subject = "NinerBuys Email Verification Code"
    body = f"""
    <p>Dear User,</p>
    <p>Thank you for signing up on NinerBuys! Please verify your email by entering the following code:</p>
    <h3>{verification_code}</h3>
    <p>The code is valid for 30 minutes.</p>
    <p>Best regards,</p>
    <p>NinerBuys Team</p>
    """

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USERNAME
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        # Connect to the Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(GMAIL_USERNAME, GMAIL_PASSWORD)  # Log in with credentials
            server.sendmail(GMAIL_USERNAME, recipient_email, msg.as_string())  # Send email
        print(f"Verification email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")