from flask import Flask, render_template, request, session
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
import os
import dotenv
import mysql.connector.pooling
import base64

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.permanent_session_lifetime = timedelta(minutes=60)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:ShinyBulbasaur20!@localhost/agoutdoors'
engine = mysql.connector.pooling.MySQLConnectionPool(
    host = 'localhost',
    user = 'root',
    password = 'ShinyBulbasaur20!',
    database = 'agoutdoors',
    auth_plugin = "mysql_native_password",
    pool_name = "agoutdoors",
    pool_size = 4,
    pool_reset_session = True
    )

def get_Db_Results(cursor):
    data=[]
    for results in cursor.stored_results(): data = results.fetchall()
    return data

def encrypt_message(message):
   #Encrypts passed in string and returns encrypted string
    the_key = os.getenv("encryption_key")
    realkey = bytes(the_key, encoding='utf-8')
    fernet=Fernet(realkey)
    encrypted_data=fernet.encrypt(str(message).encode()).decode('utf-8')
    return encrypted_data

def decrypt_message(encrypted_message):
    #decrypts passed in encrypted string and returns decrypted string
    the_key = os.getenv("encryption_key")
    realkey = bytes(the_key, encoding='utf-8')
    fernet=Fernet(realkey)
    variable=bytes(str(encrypted_message), encoding="utf-8")
    variable=fernet.decrypt(variable).decode()
    return variable

def check_if_logged_in():
    if 'currentuser' in session:
        currentuser = session['currentuser']
        return currentuser
    else:
        return None

def get_images():
    connection = engine.get_connection()
    cursor = connection.cursor() 
    cursor.callproc("select_all_images", ())
    images = get_Db_Results(cursor)
    cursor.close()
    connection.close()
    return images

def insert_into_db(table,columns,values):
    connection = engine.get_connection()
    cursor = connection.cursor() 
    cursor.callproc('insert_into_db',(table,columns,values))
    cursor.close()
    connection.close()

@app.route('/')
def index():
    currentuser = check_if_logged_in()
    return render_template('index.html',currentuser=currentuser)

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        connection = engine.get_connection()
        cursor = connection.cursor() 
        ## create account # testing purposes only
        # username = encrypt_message(username)
        # password = encrypt_message(password)
        # cursor.callproc('insert_into_db',('users','users.username,users.password',f"'{username}','{password}'"))
        ##
        ## login
        cursor.callproc("select_all", ("users",))
        users = get_Db_Results(cursor)
        for user in users:
            stored_username = user[1]
            stored_password = user[2]
            stored_username = decrypt_message(str(stored_username).replace("b'","").replace("'",""))
            if stored_username == username:
                stored_password = decrypt_message(str(stored_password).replace("b'","").replace("'",""))
                if stored_password == password:
                    cursor.close()
                    connection.close()
                    app.permanent_session_lifetime = timedelta(minutes=60)
                    session.permanent=True
                    session['currentuser'] = username
                    return render_template("login.html",success_statement='Successfully Logged In!',currentuser=username)
                else:
                    cursor.close()
                    connection.close()
                    return render_template("login.html",error_statement='Incorrect Password!')
        cursor.close()
        connection.close()
        return render_template("login.html",error_statement='Incorrect Username or Password!')
    app.permanent_session_lifetime = timedelta(minutes=60)
    session.permanent=True
    session['currentuser'] = None
    return render_template("login.html")

@app.route('/trips')
def trips():
    currentuser = check_if_logged_in()
    return render_template("trips.html",currentuser=currentuser)

@app.route("/rates")
def rates():
    currentuser = check_if_logged_in()
    return render_template("rates.html",currentuser=currentuser)

@app.route("/Contact")
def contact():
    currentuser = check_if_logged_in()
    return render_template("contact.html",currentuser=currentuser)

@app.route("/form", methods=["POST"])
def form():
    currentuser = check_if_logged_in()
    name = request.form.get("name")
    phone = request.form.get("phone_number")
    date = request.form.get("date") 
    
    if not name or not phone or not date:
        error_statement = "Name, Phone number, and Date required."
        return render_template("contact.html", error_statement = error_statement, currentuser=currentuser)
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
    return render_template("form.html", name=name, phone=phone,date=date, currentuser=currentuser)
    
@app.route("/gallery",defaults={'title':'Gallery Home','filename':'No_File'},methods=["GET"])
@app.route("/gallery/<title>",defaults={'filename':'New_File'}, methods=["GET","POST"])
@app.route("/gallery/<title>/<filename>", methods=["GET","POST"])
def gallery(title,filename):
    currentuser = check_if_logged_in()
    images = get_images()
    if request.method == 'POST':
        if title == 'Upload':
            description = request.form.get("description")
            if len(description) > 4990:
                error_statement = "Description is too long!"
                return render_template("gallery.html",images=images,error_statement=error_statement, currentuser=currentuser)
            allowed_file_types = ['.png','jpg','.jpeg','.PNG','.JPG','JPEG']
            file = request.files['file']
            if not any(str(file.filename).endswith(file_type) for file_type in allowed_file_types):
                error_statement = "Invalid File Type"
                return render_template("gallery.html",images=images,error_statement=error_statement, currentuser=currentuser)
            else:
                num_images = len(images)
                insert_into_db('gallery_entry','position,image_name,description',f"{num_images+1},'{file.filename}','{description}'")
                file.save(os.path.join('static/gallery', file.filename))
                success_statement = 'Successfully Uploaded Image to Gallery!'
                images = get_images()
                return render_template("gallery.html",images=images,success_statement=success_statement, currentuser=currentuser)
        elif title == 'Delete':
            connection = engine.get_connection()
            cursor = connection.cursor()
            cursor.callproc("select_by_value", ("gallery_entry","id",filename))
            image = get_Db_Results(cursor)
            image = image[0]
            cursor.close()
            connection.close() 
            filepath = os.path.join('static/gallery', image[2])
            if os.path.exists(filepath):
                os.remove(filepath)
                connection = engine.get_connection()
                cursor = connection.cursor()
                cursor.callproc("delete_by_value", ("gallery_entry","id",filename))
                cursor.close()
                connection.close() 
                images = get_images()
                success_statement = 'Image deleted successfully'
                return render_template("gallery.html",images=images,success_statement=success_statement, currentuser=currentuser)
            else:
                error_statement = 'Image not found'
                return render_template("gallery.html",images=images,success_statement=success_statement, currentuser=currentuser)
        elif title == 'Edit':
            currentuser = check_if_logged_in()
            if currentuser == None:
                return render_template("gallery.html",error_statement='You must be logged in to view this page!' ,images=images, currentuser=currentuser)
            connection = engine.get_connection()
            cursor = connection.cursor()
            cursor.callproc("select_by_value", ("gallery_entry","id",filename))
            image = get_Db_Results(cursor)
            image = image[0]
            cursor.close()
            connection.close()
            return render_template("image_editor.html",image=image, currentuser=currentuser)
        elif title == 'Complete Edit':
            currentuser = check_if_logged_in()
            if currentuser == None:
                images = get_images()
                return render_template("gallery.html",error_statement='You must be logged in to view this page!' ,images=images, currentuser=currentuser)
            description = request.form.get("description")
            if len(description) > 4990:
                error_statement = "Description is too long!"
                return render_template("gallery.html",images=images,error_statement=error_statement, currentuser=currentuser)
            connection = engine.get_connection()
            cursor = connection.cursor()
            cursor.callproc("update_by_value", ("gallery_entry","description",description,"id",filename))
            cursor.close()
            connection.close()
            images = get_images()
            return render_template("gallery.html",images=images, currentuser=currentuser, success_statement='Successfully Updated Image Description!')
    return render_template("gallery.html",images=images, currentuser=currentuser)

if __name__ == "__main__":
    app.run(debug=True) 