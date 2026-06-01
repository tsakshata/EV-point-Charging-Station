import random
import re
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, url_for, request, redirect, session, jsonify, flash
from DBConnection import Db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key="123"

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/find_your_charger')
def find_your_charger():
    return render_template('find_your_charger.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        feedback = request.form['message']
        db = Db()
        sql = db.insert("INSERT INTO contact_us (Name, Email, feedback_date, feedback) VALUES (%s, %s, NOW(), %s)", (name, email, feedback))
        return render_template('contact_us.html', message='Thank you for your feedback!')
    else:
        return render_template('contact_us.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == "POST":
        # Validate email input
        email = request.form.get('email', '').strip()
        if not email:
            return "Email is required", 400
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return "Invalid email format", 400

        # Check if email exists in database
        db = Db()
        user = db.selectOne("SELECT * FROM login WHERE email=%s", (email,))
        if not user:
            return "Sorry, we couldn't find an account associated with that email address.", 400

         # Send email with password reset instructions or link
        password = user['password']
        sender_email = "a97298570@gmail.com"
        sender_password = "56B50C32C322385ED3009518610638823005"
        recipient_email = email
        subject = "Password Reset for EV STATION BOOKING WEBSITE"
        content = "Your password for EV STATION BOOKING WEBSITE has been reset. Please login with your new password."
        host = "smtp.gmail.com"
        port = 465
        message = MIMEMultipart()
        message['From'] = (sender_email)
        message['To'] = (recipient_email)
        message['Subject'] = (subject)
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        try:
            with smtplib.SMTP_SSL(host, port) as server:            
                server.login("a97298570@gmail.com", "56B50C32C322385ED3009518610638823005")
                server.sendmail("a97298570@gmail.com", recipient_email, message.as_string())

                return "An email has been sent to your email address with instructions on how to reset your password."
        except smtplib.SMTPAuthenticationError:
            return "Failed to authenticate with the email server. Please check your email credentials.", 500
        except smtplib.SMTPException as e:
            return f"An error occurred while sending the email: {str(e)}", 500

    return render_template("forgot_password.html")


@app.route('/login',methods=['GET', 'POST'])
def login():
    if  'user_type' in session and session['user_type'] == "admin":
        return redirect('/admin-home')

    if request.method == "POST":
        print('form ', request.form)
        username = request.form['username']
        password = request.form['password']
        db = Db()
        ss = db.selectOne("select * from login where username=%s", (username,))
        if ss is not None:
            if check_password_hash(ss['password'], password):
                session['head'] = ""
                session['username'] = username # set the username key in the session
                if ss['usertype'] == 'admin':
                    session['user_type'] = 'admin'
                    return redirect('/admin-home')

                elif ss['usertype'] == 'user':
                    session['user_type'] = 'user'
                    session['uid'] = ss['login_id']
                    return redirect('/user-dashboard')
                else:
                    return '''<script>alert('user not found');window.location="/login"</script>'''
            else:
                return '''<script>alert('Invalid password');window.location="/login"</script>'''
        else:
            return '''<script>alert('user not found');window.location="/login"</script>'''
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('user_type',None)
    session.pop('log',None)
    session.pop('usertype',None)

    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['signupUsername']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        # Perform form validation
        if username.strip() == '':
            return redirect(url_for('register', error='Please enter a username', form_id='createAccount'))

        if email.strip() == '':
            return redirect(url_for('register', error='Please enter an email address', form_id='createAccount'))

        if password.strip() == '':
            return redirect(url_for('register', error='Please enter a password', form_id='createAccount'))

        if confirmPassword.strip() == '':
            return redirect(url_for('register', error='Please confirm the password', form_id='createAccount'))

        if password != confirmPassword:
            return redirect(url_for('register', error='Passwords do not match', form_id='createAccount'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password)
        db = Db()
        qry = db.insert("INSERT INTO login (username, password, usertype) VALUES (%s, %s, 'user')", (username, hashed_password))

        return '<script>alert("User registered"); window.location.href="/login";</script>'
    else:
        error = request.args.get('error')  # Get the error message from the URL parameters
        return render_template("login.html", error=error , form_id='createAccount')


@app.route('/admin-home')
def admin_home():
    print('session ', session)
    if session['user_type'] == 'admin':
        username = session['username'] # get the username from the session
        return render_template('admin/admin-login-dashboard.html', username=username)
    else:
        return redirect('/')


@app.route('/Manage_station')
def Manage_station():
    print('session ', session)
    if session['user_type'] == 'admin':
        db=Db()
        qry=db.select("select station_id, station_name, address, city, charger_type, available_ports, status from admin_charging_station_list")
        return render_template("admin/Manage_station.html",data=qry)
    else:
        return redirect('/')


@app.route('/view_feedback')
def view_feedback():
    print('session ', session)
    if session['user_type'] == 'admin':
        db=Db()
        ss=db.select("select * from contact_us")
        return render_template("admin/view_feedback.html",data=ss)
    else:
        return redirect('/')


@app.route("/adm_delete_station/<station_name>")
def adm_delete_station(station_name):
    print('session ', session)
    if session['user_type'] == 'admin':
        db = Db()
        qry = db.delete("DELETE FROM admin_charging_station_list WHERE Station_name = %s", (station_name,))
        return '''<script>alert('station deleted');window.location="/Manage_station"</script>'''
    else:
        return redirect('/')


@app.route("/adm_delete_feedback/<feedback>")
def adm_delete_feedback(feedback):
    print('session ', session)
    if session['user_type'] == 'admin':
        db = Db()
        qry = db.delete("delete from contact_us where Sl_no='"+feedback+"'")
        return '''<script>alert('feedback deleted');window.location="/view_feedback"</script>'''
    else:
        return redirect('/')


@app.route('/user-list')
def user_list():
    print('session ', session)
    if session['user_type'] == 'admin':
        db=Db()
        qry = db.select("SELECT * FROM user")
        return render_template("admin/user-list.html",data=qry)
    else:
        return redirect('/')


@app.route("/adm_delete_user/<user_id>")
def adm_delete_user(user_id):
    print('session ', session)
    if session['user_type'] == 'admin':
        db = Db()
        qry = db.delete("delete from user where user_id='"+user_id+"'")
        return '''<script>alert('user deleted');window.location="/user-list"</script>'''
    else:
        return redirect('/')


@app.route('/view_booking')
def view_booking():
    if session.get('user_type') != 'admin':
        return redirect('/')

    db = Db()
    raw_bookings = db.select("""
        SELECT 
            b.booking_id,
            b.Booking_date,
            b.Time_from,
            b.Time_to,
            b.City,
            b.Station_name,
            b.Available_ports,
            b.login_id  # Changed from l.username to b.login_id
        FROM booking b
        ORDER BY b.Booking_date DESC
    """)

    bookings = []
    for b in raw_bookings:
        # Convert timedelta to time
        time_from = (datetime.min + b['Time_from']).time()
        time_to = (datetime.min + b['Time_to']).time()
        
        bookings.append({
            'booking_id': b['booking_id'],
            'booking_date': b['Booking_date'].strftime('%Y-%m-%d'),
            'time_from': time_from.strftime('%H:%M'),
            'time_to': time_to.strftime('%H:%M'),
            'city': b['City'],
            'station_name': b['Station_name'],
            'available_ports': b['Available_ports'],
            'user_name': b['login_id']  # Now showing login_id instead of username
        })

    return render_template('admin/view_booking.html', bookings=bookings)

@app.route("/adm_delete_booking/<Booking_id>")
def adm_delete_booking(Booking_id):
    print('session ', session)
    if session['user_type'] == 'admin':
        db = Db()
        qry = db.delete("delete from booking where Booking_id='"+Booking_id+"'")
        return '''<script>alert('booking deleted');window.location="/view_booking"</script>'''
    else:
        return redirect('/')


@app.route('/user-dashboard')
def user_dashboard():
    try:
        db = Db()
        bookings = db.select("SELECT * FROM booking WHERE login_id = %s ORDER BY Booking_date DESC", (session['uid'],))
        return render_template("user/user-login-dashboard.html", bookings=bookings, username=session['username'])
    except Exception as e:
        flash('Error loading dashboard', 'error')
        return render_template("user/user-login-dashboard.html", bookings=[], username=session['username'])


@app.route('/usr_delete_booking/<int:booking_id>')
def usr_delete_booking(booking_id):
    if 'user_type' in session and session['user_type'] == "user":
        db = Db()
        
        # Delete the booking for the specific user and booking_id
        db.delete("DELETE FROM booking WHERE booking_id = %s AND login_id = %s", (booking_id, session['uid']))
        
        return '''<script>alert('Booking deleted');window.location="/user-dashboard"</script>'''
    else:
        return redirect('/user-dashboard')


@app.route('/user_find_your_charger', methods=['GET', 'POST'])
def user_find_your_charger():
    if 'user_type' in session and session['user_type'] == 'user':
        if request.method == 'POST':
            city = request.form.get('City')
            charger_type = request.form.get('Charger_type')
            db = Db()
            qry = db.select("select Station_name, Address, Charger_type, Available_ports from admin_charging_station_list where City = %s and Charger_type = %s", (city, charger_type))
            return render_template('user/station_search.html', data=qry)       
        else:
            return render_template('user/user_find_your_charger.html')
    else:
        return redirect('/')


@app.route('/search_stations', methods=['POST'])
def search_stations():
    # Get the form data
    City = request.form.get('City')
    Charger_type = request.form.get('Charger_type')

    # Redirect to the station_list page with the city and charger_type as URL parameters
    return redirect(url_for('station_search', City=City, Charger_type=Charger_type))


@app.route('/station_search', methods=['GET'])
def station_search():
    if 'user_type' in session and session['user_type'] == 'user':
        City = request.args.get('City')
        Charger_type = request.args.get('Charger_type')
        # Query your MySQL database using the city and charge_type variables
        db = Db()
        sql = "select * from admin_charging_station_list where City = %s and Charger_type = %s"
        ss = db.select(sql, (City, Charger_type))

        # Return the results to the user in a new template
        return render_template('user/station_search.html', data=ss, City=City, Charger_type=Charger_type)
    else:
        return redirect('/')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        Station_name = request.form['Station_name']
        City = request.form['City']
        Available_ports = request.form['Available_ports']
        return redirect(url_for('booking_form',  Station_name=Station_name, City=City, Available_ports=Available_ports))
    else:
        # handle GET request to display the form
        Station_name = request.args.get('Station_name')
        City = request.args.get('City')
        Available_ports = request.args.get('Available_ports')
        return redirect(url_for('booking_form', Station_name=Station_name, City=City, Available_ports=Available_ports))


@app.route('/booking-form', methods=['GET'])
def booking_form():
    city = request.args.get('City')
    available_ports = request.args.get('Available_ports')
    station_name = request.args.get('Station_name')
    db = Db()
    station_data = db.select("select * from admin_charging_station_list where Station_name = %s", (station_name,))
    session['station_data'] = station_data[0] if station_data else None
    if 'station_data' in session and session['station_data']:
        return render_template('/user/booking_form.html', city=city, available_ports=available_ports)
    else:
        return redirect(url_for('station_search'))


@app.route('/book', methods=['POST'])
def book():
    if 'user_type' in session and session['user_type'] == 'user':
        # get the form data submitted by the user
        station_name = request.form['Station_name']
        city = request.form['City']
        available_ports = request.form['Available_ports']
        booking_date = request.form['Booking_date']
        time_from = request.form['Time_from']
        time_to = request.form['Time_to']
        login_id = session['uid']


        db = Db()

        # get the current timestamp
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # insert the booking data into the MySQL table
        sql = "insert into booking (Station_name, City, Available_ports, Booking_date, Time_from, Time_to, Created_id, login_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        booking_id = db.insert(sql, (station_name, city, available_ports, booking_date, time_from, time_to, created_at, login_id))

        # redirect the user to their dashboard
        return render_template("user/user-login-dashboard.html", data={
            'Station_name': station_name,
            'City': city,
            'Available_ports': available_ports,
            'Booking_date': booking_date,
            'Time_from': time_from,
            'Time_to': time_to,
            'Created_id': created_at,
            'Booking_id': booking_id
        })
    else:
        return redirect('/booking-form')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)