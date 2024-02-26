from flask import Flask, render_template, request 
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


#add gallery with database, add video archive. My boat page

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trips')
def trips():
    return render_template("trips.html")

@app.route("/rates")
def rates():
    return render_template("rates.html")

@app.route("/Contact")
def contact():
    return render_template("contact.html")

@app.route("/form", methods=["POST"])
def form():
    name = request.form.get("name")
    phone = request.form.get("phone_number")
    date = request.form.get("date") 
    
    if not name or not phone or not date:
        error_statement = "Name, Phone number, and Date required."
        return render_template("contact.html", error_statement = error_statement)
    else:
        message = name + " would like to book a fishing trip with Andy Gustafson on " + date + ". Their phone number is " + phone 
    smtp_server = 'smtp.gmail.com'
    port = 587 # or 465 for SSL/TLS encrypted connection
    smtp_username = 'agoutdoorswebsite@gmail.com'
    smtp_password = 'ntzwltjayqcqkpcx'
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    msg = MIMEMultipart()
    msg['From'] = 'agoutdoorswebsite@gmail.com'
    msg['To'] = 'andymgustafson@yahoo.com'
    msg['Subject'] = 'Fishing Trip Request'
    msg.attach(MIMEText(message, 'plain'))
    server.sendmail(smtp_username, 'andymgustafson@yahoo.com', msg.as_string())
    server.quit()
    return render_template("form.html", name=name, phone=phone,date=date)
    
 
if __name__ == "__main__":
    app.run(debug=True) 