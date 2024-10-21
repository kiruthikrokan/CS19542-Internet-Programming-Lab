from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret key for session management and flash messages

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update this connection string as needed
db = client['user_data']  # Database name
users_collection = db['users']
absentees_collection = db['absentees']

# Function to add a new user to the MongoDB (signup process)
def add_user(username, email, password):
    try:
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        
        # Insert the new user's data into the MongoDB collection
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password
        })
        return True  # Return True if the signup was successful

    except Exception as e:
        print(f"Error: {e}")
        return False  # Return False if there's an error (e.g., duplicate username/email)

# Function to check user credentials (login process)
def check_user_credentials(username, password):
    # Fetch the user's data from the MongoDB collection
    user = users_collection.find_one({'username': username})

    if user:
        stored_password = user['password']
        # Check if the provided password matches the stored hashed password
        return check_password_hash(stored_password, password)
    else:
        return False  # Return False if the user is not found

# Function to add absentee information
def add_absentee(roll_number, absence_date):
    # Check if the student is already marked absent on the given date
    existing_absentee = absentees_collection.find_one({'roll_number': roll_number, 'absence_date': absence_date})

    if existing_absentee:
        # Student is already marked absent for this date, return False
        return False

    # Add the absentee to the database with the specified date
    absentees_collection.insert_one({
        'roll_number': roll_number,
        'absence_date': absence_date
    })
    return True

# Function to fetch the list of absentees from the database
def get_absentees():
    absentees = absentees_collection.find({}, {'_id': 0, 'roll_number': 1, 'absence_date': 1})  # Fetch roll numbers and absence dates
    absentees_list = [{'roll_number': absentee['roll_number'], 'absence_date': absentee['absence_date']} for absentee in absentees]  # Convert to list of dictionaries
    return absentees_list  # Return the list of absentees with roll numbers and absence dates

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user credentials are correct
        if check_user_credentials(username, password):
            return redirect(url_for('rokapip'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Attempt to add the new user to the database
        if add_user(username, email, password):
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists. Please try a different one.', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/rokapip', methods=['POST', 'GET'])
def rokapip():
    return render_template('rokapip.html')

@app.route('/attendance', methods=['POST', 'GET'])
def attendance():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        absence_date = datetime.now().strftime('%Y-%m-%d')  # Automatically use the system date in 'YYYY-MM-DD' format

        # Attempt to add the absent student with the absence date to the database
        if add_absentee(roll_number, absence_date):
            flash(f'Attendance marked as absent for roll number: {roll_number} on {absence_date}', 'success')
        else:
            flash('Roll number already marked as absent.', 'danger')

        return redirect(url_for('attendance'))

    return render_template('attendance.html')

@app.route('/view_absentees', methods=['GET'])
def view_absentees():
    absentees = get_absentees()  # Fetch the list of absentees
    return jsonify(absentees)  # Return the list as JSON

if __name__ == '__main__':
    app.run(debug=True)
