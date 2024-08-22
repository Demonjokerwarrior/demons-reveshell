from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Secret key for session management
app.secret_key = 'joker'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'demon'
app.config['MYSQL_PASSWORD'] = 'joker'
app.config['MYSQL_DB'] = 'hunter'

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id, password FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account and password == account['password']:
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('cart', None)  # Clear the cart on logout
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password, address, email, phone_number) VALUES (%s, %s, %s, %s, %s)', (username, password, address, email, phone_number))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/process_order', methods=['POST'])
def process_order():
    # Process the order here
    return 'Order processed successfully'


@app.route('/shop')
def shop():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return render_template('shop.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}
    cart = session['cart']
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    session['cart'] = {str(k): v for k, v in cart.items()}  # Ensure keys are strings
    return redirect(url_for('shop'))

@app.route('/cart')
def cart():
    if 'cart' not in session or not isinstance(session['cart'], dict):
        return render_template('cart.html', products=[])

    product_ids = session['cart'].keys()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products WHERE product_id IN ({})'.format(','.join(map(str, product_ids))))
    products = cursor.fetchall()

    # Add quantity to each product
    for product in products:
        product['quantity'] = session['cart'][str(product['product_id'])]
    
    return render_template('cart.html', products=products)

@app.route('/remove_product', methods=['GET'])
def remove_product():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    return render_template('remove_product.html', products=products)

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM products WHERE product_id = %s', (product_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('remove_product'))
    
@app.route('/remove_user', methods=['GET'])
def remove_user():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    return render_template('remove_users.html', users=users)
    
    
    
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    cursor = mysql.connection.cursor()

    # Delete orders associated with the user
    cursor.execute('DELETE FROM orders WHERE user_id = %s', (user_id,))

    # Delete the user
    cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
    
    mysql.connection.commit()
    cursor.close()
    
    return redirect(url_for('remove_user'))


    
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        if str(product_id) in cart:
            cart.pop(str(product_id))
            session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'loggedin' in session:
        msg = ''
        if request.method == 'POST':
            order_details = ','.join(f"{pid}:{quantity}" for pid, quantity in session['cart'].items())
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO orders (user_id, order_details) VALUES (%s, %s)', (session['user_id'], order_details))
            mysql.connection.commit()
            session.pop('cart', None)
            msg = 'Order confirmed!'
        return render_template('checkout.html', msg=msg)
    return redirect(url_for('login'))

# Directory to store uploaded images

app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']

        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty part without a filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"/static/{filename}"  # Assuming the files are stored in the 'static' folder

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO products (product_name, product_price, image_url) VALUES (%s, %s, %s)', (product_name, product_price, image_url))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('add_product'))  # Redirect to the add_product page after adding a product

    return render_template('add_product.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    
    for order in orders:
        order_details = order['order_details'].split(',')
        detailed_order = []
        
        for item in order_details:
            product_id, quantity = item.split(':')
            cursor.execute('SELECT product_name FROM products WHERE product_id = %s', [product_id])
            product = cursor.fetchone()
            if product:
                detailed_order.append({
                    'product_name': product['product_name'],
                    'quantity': quantity
                })
        
        order['detailed_order'] = detailed_order
    
    return render_template('admin_dashboard.html', orders=orders)


if __name__ == '__main__':
    app.run(debug=True)
