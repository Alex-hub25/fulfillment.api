
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from hashlib import sha256
from time import sleep
import requests


app = Flask(__name__)
# Change this to your secret key (it can be anything, it's for extra protection)
app.secret_key = 'my secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL
mysql = MySQL(app)

@app.route('/about' )
def about():
    return render_template('about.htm')

@app.route('/', methods=['GET', 'POST'])
def login():
    # Output a message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.htm', msg=msg)

@app.route('/logout')
def logout():

    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists, please login'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'        
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.htm', msg=msg)

# Connect to Raspberry Pi****
# Add constant refresh signaling pi status  
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        try:
            raspberry_pi_url = "http://192.168.1.109:5000/"
            response = requests.get(raspberry_pi_url)  # Use requests.get to make an HTTP GET request
            if response.status_code == 200:
                pi_data = response.json()  # Assuming the Raspberry Pi sends JSON dat
                msg = "Connected"
            else:
                pi_data = {}
                msg = f"Failed to connect to Raspberry Pi. Status code: {response.status_code}"
        except Exception as e:
            pi_data = {}
            msg = f"Error connecting to Raspberry Pi: {str(e)}"

        return render_template('home.htm', username=session['username'], pi_data=pi_data, msg=msg)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():

    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        try:
            raspberry_pi_url = "http://192.168.1.109:5000/"
            response = requests.get(raspberry_pi_url)  # Use requests.get to make an HTTP GET request
            if response.status_code == 200:
                pi_data = response.json()  # Assuming the Raspberry Pi sends JSON dat
                msg = f"Connected  {raspberry_pi_url}"
            else:
                pi_data = {}
                msg = f"Not Connected. Status code: {response.status_code}"
        except Exception as e:
            pi_data = {}
            msg = f"Error connecting to Raspberry Pi: {str(e)}"

        return render_template('profile.htm', account=account, pi_data=pi_data, msg=msg)
    return redirect(url_for('login'))

#works
#manual option to set up freight shipment ****
#Future Requirments:
#Input multiple shipments with the same name
#Offer check boxes for 'commerical, do not stack, liftgate, ect'
#*IN SQL* organize like, Delivery, package, Pickup
#default pickup location

@app.route('/shipments', methods=['GET', 'POST'])
def shipments():
    if 'loggedin' in session:
        msg = ''        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM pickup ORDER BY idpickup DESC LIMIT 1')
        rows = cursor.fetchall()

        if request.method == 'POST' and 'LastName_pickup' in request.form and 'FirstName_pickup' in request.form and 'Address_pickup' in request.form and 'City_pickup' in request.form and 'State_pickup' in request.form and 'PostalCode_pickup' in request.form and 'LastName_delivery' in request.form and 'FirstName_delivery' in request.form and 'Address_delivery' in request.form and 'City_delivery' in request.form and 'State_delivery' in request.form and 'PostalCode_delivery' in request.form and 'weight' in request.form and 'length' in request.form and 'width' in request.form and 'height' in request.form and 'quantity' in request.form and 'description' in request.form:
                
                # Create variables for easy access
            LastName_pickup = request.form['LastName_pickup']
            FirstName_pickup = request.form['FirstName_pickup']
            Address_pickup = request.form['Address_pickup']
            City_pickup = request.form['City_pickup']
            State_pickup = request.form['State_pickup']
            PostalCode_pickup = request.form['PostalCode_pickup']
            LastName_delivery = request.form['LastName_delivery']
            FirstName_delivery = request.form['FirstName_delivery']
            Address_delivery = request.form['Address_delivery']
            City_delivery = request.form['City_delivery']
            State_delivery = request.form['State_delivery']
            PostalCode_delivery = request.form['PostalCode_delivery']
            weight = request.form['weight']
            length = request.form['length']
            width = request.form['width']
            height = request.form['height']
            quantity = request.form['quantity']
            description = request.form['description']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            rows = ('INSERT INTO shipments VALUES (idshipments, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')
            values = [ (LastName_pickup, FirstName_pickup, Address_pickup, City_pickup, State_pickup, PostalCode_pickup, LastName_delivery, FirstName_delivery, Address_delivery, City_delivery, State_delivery, PostalCode_delivery, weight, length, width, height, quantity, description)]
            cursor.executemany(rows, values)
            mysql.connection.commit()
            # mysql.close()
            msg = 'shipment successfuly logged!'      
            
            return redirect(url_for('carriers'))


        elif request.method == 'POST':
                    # Form is empty... (no POST data)
                    msg = 'Please fill out the form!'
                # Show registration form with message (if any)

        return render_template('shipments.htm', msg=msg)    

        # return render_template('carriers.htm')
    
    return redirect(url_for('login'))

#works
#directs users to carrier list, only accessable after shipment information is entered.****
#Future Requirements: 
# Api for recent shipment info to be listed in table w/ editable options
# APi to freight companies pricing, connection to set up shipment
# Filter option
@app.route('/carriers', methods=['GET', 'POST'])
def carriers():
    if 'loggedin' in session:
        msg = ''
        # Create Recent shipment data to pull from later
        # Allow data to be edited SQL Update 
        # # Show data in table
        # Shows most recent data in table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shipments ORDER BY idshipments DESC LIMIT 1')
        rows = cursor.fetchall()
        if request.method == 'POST' and 'LastName_pickup' in request.form and 'FirstName_pickup' in request.form and 'Address_pickup' in request.form and 'City_pickup' in request.form and 'State_pickup' in request.form and 'PostalCode_pickup' in request.form and 'LastName_delivery' in request.form and 'FirstName_delivery' in request.form and 'Address_delivery' in request.form and 'City_delivery' in request.form and 'State_delivery' in request.form and 'PostalCode_delivery' in request.form and 'weight' in request.form and 'length' in request.form and 'width' in request.form and 'height' in request.form and 'quantity' in request.form and 'description' in request.form:
            #Create Variable for easy access
            idshipment = rows[0]['idshipments'] if rows else None
            LastName_pickup = request.form['LastName_pickup']
            FirstName_pickup = request.form['FirstName_pickup']
            Address_pickup = request.form['Address_pickup']
            City_pickup = request.form['City_pickup']
            State_pickup = request.form['State_pickup']
            PostalCode_pickup = request.form['PostalCode_pickup']
            LastName_delivery = request.form['LastName_delivery']
            FirstName_delivery = request.form['FirstName_delivery']
            Address_delivery = request.form['Address_delivery']
            City_delivery = request.form['City_delivery']
            State_delivery = request.form['State_delivery']
            PostalCode_delivery = request.form['PostalCode_delivery']
            weight = request.form['weight']
            length = request.form['length']
            width = request.form['width']
            height = request.form['height']
            quantity = request.form['quantity']
            description = request.form['description']

            input_data = (
                LastName_pickup, FirstName_pickup, Address_pickup, City_pickup, State_pickup, PostalCode_pickup,
                LastName_delivery, FirstName_delivery, Address_delivery, City_delivery, State_delivery, PostalCode_delivery,
                weight, length, width, height, quantity, description, idshipment
            )

            sql_update_query = """
                UPDATE shipments 
                SET 
                    LastName_pickup = %s, FirstName_pickup = %s, Address_pickup = %s, City_pickup = %s, State_pickup = %s, PostalCode_pickup = %s, 
                    LastName_delivery = %s, FirstName_delivery = %s, Address_delivery = %s, City_delivery = %s, State_delivery = %s, PostalCode_delivery = %s, 
                    weight = %s, length = %s, width = %s, height = %s, quantity = %s, description = %s 
                WHERE idshipments = %s
             """
            cursor.execute(sql_update_query, input_data)
            mysql.connection.commit()
            data = cursor.fetchall()
            msg = 'Shipment successfully updated!'
            
        elif request.method == 'POST':
            msg = 'Please fill out the form!'

            return jsonify(data)
        return render_template('carriers.htm', rows=rows, msg=msg)
    return redirect('login')

@app.route('/ashipments', methods=['GET', 'POST'])
def ashipments():
    if 'loggedin' in session:
        msg = ''
        # Create Recent shipment data to pull from later
        # Allow data to be edited SQL Update 
        # # Show data in table
        # Shows most recent data in table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM label ORDER BY id DESC LIMIT 1')
        rows = cursor.fetchall()
        if request.method == 'POST' and 'invoice_number' in request.form and 'order_number' in request.form and 'total_balance' in request.form and 'invoice_date' in request.form and 'due_date' in request.form and 'sender' in request.form and 'receiver' in request.form:
            #Create Variable for easy access
            id = rows[0]['id'] if rows else None
            invoice_number = request.form['invoice_number']
            order_number = request.form['order_number']
            total_balance = request.form['total_balance']
            invoice_date = request.form['invoice_date']
            due_date = request.form['due_date']
            sender = request.form['sender']
            receiver = request.form['receiver']

            input_data = (
                id, invoice_number, order_number, total_balance, invoice_date, due_date, sender, receiver
            )

            sql_update_query = """
                UPDATE shipments 
                SET 
                    invoice_number = %s, order_number = %s, total_balance = %s, invoice_date = %s, due_date = %s, sender = %s, receiver = %s 
                WHERE id = %s
             """
            cursor.execute(sql_update_query, input_data)
            mysql.connection.commit()
            data = cursor.fetchall()
            msg = 'Shipment successfully updated!'
            
        elif request.method == 'POST':
            msg = 'Please fill out the form!'

            return jsonify(data)
        return render_template('ashipments.htm', rows=rows, msg=msg)
    return redirect('login')

@app.route('/eshipments', methods=['GET', 'POST'])
def eshipments():
    if 'loggedin' in session:
        msg = ''
        # Create Recent shipment data to pull from later
        # Allow data to be edited SQL Update 
        # # Show data in table
        # Shows most recent data in table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM label ORDER BY id DESC LIMIT 1')
        rows = cursor.fetchall()
        if request.method == 'POST' and 'invoice_number' in request.form and 'order_number' in request.form and 'total_balance' in request.form and 'invoice_date' in request.form and 'due_date' in request.form and 'sender' in request.form and 'receiver' in request.form:
            #Create Variable for easy access
            id = rows[0]['id'] if rows else None
            invoice_number = request.form['invoice_number']
            order_number = request.form['order_number']
            total_balance = request.form['total_balance']
            invoice_date = request.form['invoice_date']
            due_date = request.form['due_date']
            sender = request.form['sender']
            receiver = request.form['receiver']

            input_data = (
                id, invoice_number, order_number, total_balance, invoice_date, due_date, sender, receiver
            )

            sql_update_query = """
                UPDATE shipments 
                SET 
                    invoice_number = %s, order_number = %s, total_balance = %s, invoice_date = %s, due_date = %s, sender = %s, receiver = %s 
                WHERE id = %s
             """
            cursor.execute(sql_update_query, input_data)
            mysql.connection.commit()
            data = cursor.fetchall()
            msg = 'Shipment successfully updated!'
            
        elif request.method == 'POST':
            msg = 'Please fill out the form!'

            return jsonify(data)
        return render_template('eshipments.htm', rows=rows, msg=msg)
    return redirect('login')


#works
@app.route('/fulfilled', methods=['GET', 'Post'])
def fulfilled():


    if 'loggedin' in session:
        msg = ''
       
        
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        # account = cursor.fetchone() 

           
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM shipments')
        rows = cursor.fetchall()

        return render_template('fulfilled.htm', msg=msg, rows=rows)
    return redirect('login')

@app.route('/config', methods=['GET', 'Post'])
def config():
    if 'loggedin' in session:


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        return render_template('config.htm', account=account)
    return redirect('login')

@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        return render_template('billing.htm', account=account)
    return redirect('login') 

@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        return render_template('tracking.htm', account=account)
    return redirect('login') 

@app.route('/claims', methods=['GET', 'POST'])
def claims():
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        return render_template('claims.htm', account=account)
    return redirect('login') 

@app.route('/pvision', methods=['GET', 'POST'])
def pvision():
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        return render_template('pvision.htm', account=account)
    return redirect('login') 

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=True)



#Check render template and redirect install*****
    # return render_template('index.html', msg='')

# @app.route('/pythonlogin', methods=['GET', 'POST'])
# def login():
#     # Output a message if something goes wrong...
#     # Check if "username" and "password" POST requests exist (user submitted form)
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         # Create variables for easy access
#         username = request.form['username']
#         password = request.form['password']
#         # Check if account exists using MySQL
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
#         # Fetch one record and return result
#         account = cursor.fetchone()
#         # If account exists in accounts table in out database
#         if account:
#             # Create session data, we can access this data in other routes
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             # Redirect to home page
#             return 'Logged in successfully!'
#         else:
#             # Account doesnt exist or username/password incorrect
#             msg = 'Incorrect username/password!'
#     # Show the login form with message (if any)
#     return render_template('index.html')


#     # http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
# @app.route("/register", methods=['GET', 'POST']) #What is the route
# def register(): #define the route
#     # Output message if something goes wrong...
#     msg = '' #define local variable
#     # Check if "username", "password" and "email" POST requests exist (user submitted form)
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form: #start if, elif, else block
#         # Create variables for easy access
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#                 # Check if account exists using MySQL
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
#         account = cursor.fetchone()
#         # If account exists show error and validation checks
#         if account:
#             msg = 'Account already exists!'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address!'
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             msg = 'Username must contain only characters and numbers!'
#         elif not username or not password or not email:
#             msg = 'Please fill out the form!'
#         else:
#             # Hash the password
#             hash = password + app.secret_key
#             hash = hashlib.sha1(hash.encode())
#             password = hash.hexdigest()
#             # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
#             cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
#             mysql.connection.commit()
#             msg = 'You have successfully registered!'
#     elif request.method == 'POST':
#         # Form is empty... (no POST data)
#         msg = 'Please fill out the form!'
#     # Show registration form with message (if any)
#     return render_template('register.html', msg=msg)


# @app.route('/pythonlogin/home')
# def home():
#     # Check if the user is logged in
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         return render_template('home.html', username=session['username'])
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))


# @app.route('/packages', methods=['GET', 'POST'])
# def packages():
#     if 'loggedin' in session:
#         msg = ""
#         #Packages (WORKS)
#         if request.method == 'POST' and 'weight' in request.form and 'length' in request.form and 'width' in request.form and 'height' in request.form and 'quantity' in request.form:
#             weight = request.form['weight']
#             length = request.form['length']
#             width = request.form['width']
#             height = request.form['height']
#             quantity = request.form['quantity']
#             cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#             cursor.execute('SELECT * FROM packages WHERE weight = %s', (weight,))
#             packages = cursor.fetchone()
#             if packages:
#                 msg = 'package found'

#             else:
#                 cursor.execute('INSERT INTO packages VALUES (idpackages, %s, %s, %s, %s, %s)', (weight, length, width, height, quantity))
#                 mysql.connection.commit()
#                 msg = 'package saved'
#         elif request.method == 'POST':
#             msg = 'please fill out form'
#     return render_template('shipments.htm', msg=msg)

# @app.route('/pickup', methods=['GET', 'POST'])
# def pickup():
#     if 'loggedin' in session:
#         msg = ''

#         #Delivery
#         if request.method == 'POST' and 'LastName' in request.form and 'FirstName' in request.form and 'Address' in request.form and 'City' in request.form and 'State' in request.form and 'PostalCode' in request.form:
#                 # Create variables for easy access
#                 LastName = request.form['LastName']
#                 FirstName = request.form['FirstName']
#                 Address = request.form['Address']
#                 City = request.form['City']
#                 State = request.form['State']
#                 PostalCode = request.form['PostalCode']
#                 # Check if account exists using MySQL
#                 cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#                 cursor.execute('SELECT * FROM pickup WHERE lastname = %s', (LastName,))
#                 pickup = cursor.fetchone()
#                 # If account exists show error and validation checks
#                 if pickup:
#                     msg = 'shipment found'
#                 else:
#                     # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
#                     cursor.execute('INSERT INTO pickup VALUES (idpickup, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s)', (LastName, FirstName, Address, City, State, PostalCode))
#                     mysql.connection.commit()
#                     msg = 'Pickup Address Saved!'        
#         elif request.method == 'POST':
#                 # Form is empty... (no POST data)
#             msg = 'Please fill out the form!'
#             # Show registration form with message (if any)
#         return render_template('shipments.htm', msg=msg)

#     return redirect(url_for('login'))