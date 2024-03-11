from flask import Flask, render_template, request 
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def encrypt_message(message):
    key = os.getenv('encryption_key')
    cipher = Fernet(key)
    encrypt_message = cipher.encrypt(message.encode())
    return encrypt_message

def decrypt_message(encrypted_message):
    key = os.getenv('encryption_key')
    cipher = Fernet(key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login",methods=['POST','GET'])
def login():
    return render_template("login.html")

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
    
@app.route("/gallery",defaults={'title':'Gallery Home','filename':'No_File'},methods=["GET"])
@app.route("/gallery/<title>",defaults={'filename':'New_File'}, methods=["GET","POST"])
@app.route("/gallery/<title>/<filename>", methods=["GET","POST"])
def gallery(title,filename):
    images = os.listdir('static/gallery')
    if request.method == 'POST':
        if title == 'Upload':
            allowed_file_types = ['.png','jpg','.jpeg']
            file = request.files['file']
            if not any(str(file.filename).endswith(file_type) for file_type in allowed_file_types):
                error_statement = "Invalid File Type"
                return render_template("gallery.html",images=images,error_statement=error_statement)
            else:
                file.save(os.path.join('static/gallery', file.filename))
                success_statement = 'Successfully Uploaded Image to Gallery!'
                images = os.listdir('static/gallery')
                return render_template("gallery.html",images=images,success_statement=success_statement)
        elif title == 'Delete':
            filepath = os.path.join('static/gallery', filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                images = os.listdir('static/gallery')
                success_statement = 'Image deleted successfully'
                return render_template("gallery.html",images=images,success_statement=success_statement)
            else:
                error_statement = 'Image not found'
                return render_template("gallery.html",images=images,success_statement=success_statement)
    return render_template("gallery.html",images=images)

if __name__ == "__main__":
    app.run(debug=True) 