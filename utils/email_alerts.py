import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
from string import Template

# load environment variables from.env file
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email_alert(
        to_email: str, 
        stock: str, 
        current_price: float, 
        target_price: float) -> None:
    
    """Sends an email notification when a stock hits the target price.

    Args:
        to_email (str): The recipient's email address.
        stock (str): The stock symbol (e.g., AAPL, MSFT).
        current_price (float): The current price of the stock.
        target_price (float): The target price that triggered the alert.
    """

    # check if a recipient email is provided
    if not to_email:
        print("⚠️ No recipient email provided. Skipping email alert.")
        return

    # create email message
    message = EmailMessage()
    message["From"] = EMAIL_USER
    message["To"] = to_email
    message["Subject"] = f"📈 Stock Alert: {stock} has hit ${current_price:.2f}!"

    # construct path to the email template file
    template_path = os.path.join(os.path.dirname(__file__), "templates/email_template.html")

    # load and populate the HTML template
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())
        html_content = template.substitute(stock=stock, current_price=f"{current_price:.2f}", target_price=target_price)
    
    # if template not found
    except FileNotFoundError:
        html_content = f"<p>{stock} has hit ${current_price:.2f}, reaching your target of ${target_price:.2f}.</p>"

    # add the HTML content to the email
    message.add_alternative(html_content, subtype="html")

    # create a secure SSL context for sending the email
    context = ssl.create_default_context()
    try:
        # connect to the gmail SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, message.as_string())
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# test
if __name__ == "__main__":
    send_email_alert(EMAIL_USER, "AAPL", 224.05, 224.59)