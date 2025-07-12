from flask import Flask, flash, render_template, request, redirect, session, url_for, abort
import shelve
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Ensure the directory exists for saving QR codes if needed
os.makedirs('static/qrcodes', exist_ok=True)


@app.route('/Aboutus')
def Aboutus():
    return render_template('Aboutus.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/')
def home():
    user_email = session.get('email')  # Get the email from the session if the user is logged in
    return render_template('home.html', user_email=user_email)


# abby codes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with shelve.open('user_data.db') as db:
            if email in db:
                user = db[email]
                if user['password'] == password:
                    session['email'] = email
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Incorrect password. Please try again.', 'danger')
                    return render_template('login.html', error="Incorrect password.")
            else:
                flash('Email not found. Please sign up.', 'warning')
                return render_template('login.html', error="Email not found.")
    return render_template('login.html')

# Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with shelve.open('user_data.db') as db:
            if email in db:
                flash('Email already registered. Please log in.', 'warning')
                return render_template('login.html', error="Email already registered.")
            else:
                db[email] = {'name': request.form['name'], 'password': password}
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

# Profile Route
@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    with shelve.open('user_data.db') as db:
        user_data = db[user_email] if user_email in db else {}

    return render_template('profile.html', user_data={'name': user_data.get('name', ''), 'email': user_email})

# Update Profile Route
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    new_name = request.form['name']
    new_email = request.form['email']
    new_password = request.form['password']

    with shelve.open('user_data.db', writeback=True) as db:
        if user_email in db:
            user_data = db[user_email]
            user_data['name'] = new_name
            user_data['email'] = new_email
            if new_password:
                user_data['password'] = new_password

            if new_email != user_email:
                db[new_email] = user_data
                del db[user_email]
                session['email'] = new_email  # Update session with new email

            flash('Profile updated successfully!', 'success')
        else:
            flash('User not found. Please log in again.', 'danger')

    return redirect(url_for('profile'))

# Delete Account Route
@app.route('/delete_account')
def delete_account():
    if 'email' not in session:
        return redirect(url_for('login'))

    user_email = session['email']
    with shelve.open('user_data.db') as db:
        if user_email in db:
            del db[user_email]
            session.pop('email', None)
            flash('Your account has been deleted.', 'info')

    return redirect(url_for('home'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('email', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to home page without flash message


# lae's codes
def get_db():
    return shelve.open('faq.db')
@app.route('/faq', methods=['GET', 'POST'])
def faq():
    with get_db() as db:
        faqs = db.get('FAQs', [])
        if request.method == 'POST':
            question = request.form.get('question')
            description = request.form.get('description')  # Optional field

            if question:
                faq_entry = {
                    'question': question,
                    'description': description if description else None,
                    'likes': 0,
                    'comments': []
                }
                faqs.append(faq_entry)
                db['FAQs'] = faqs
                flash('FAQ added successfully!', 'success')
                return redirect(url_for('faq'))
            else:
                flash('Question is required.', 'danger')
        # Pass logged-in email to the template for conditional rendering
        return render_template('faq.html', faqs=faqs, logged_in_email=session.get('email'))

@app.route('/add_comment/<int:faq_id>', methods=['POST'])
def add_comment(faq_id):
    logged_in_user_email = session.get('email')

    if logged_in_user_email != 'staff@gmail.com':
        flash('Only staff members can add comments.', 'danger')
        return redirect(url_for('faq'))

    db = get_db()
    faqs = db.get('FAQs', [])

    if not (0 <= faq_id < len(faqs)):
        db.close()
        abort(404)

    comment = request.form.get('comment')
    user = request.form.get('user', 'Admin')
    is_owner = request.form.get('is_owner') == 'true'

    if comment:
        faqs[faq_id]['comments'].append({'user': user, 'comment': comment, 'is_owner': is_owner})
        db['FAQs'] = faqs
        flash('Comment added successfully!', 'success')

    db.close()
    return redirect(url_for('faq'))


@app.route('/delete_faq/<int:faq_id>', methods=['POST'])
def delete_faq(faq_id):
    db = get_db()
    faqs = db.get('FAQs', [])
    
    if 0 <= faq_id < len(faqs):
        del faqs[faq_id]
        db['FAQs'] = faqs
        flash('FAQ deleted successfully!', 'success')
    
    db.close()
    return redirect(url_for('faq'))

@app.route('/edit_faq/<int:faq_id>', methods=['GET', 'POST'])
def edit_faq(faq_id):
    with get_db() as db:
        faqs = db.get('FAQs', [])
        
        if request.method == 'POST':
            email = request.form.get('email')
            if email == 'staff@gmail.com':
                # Ensure data is updated
                faqs[faq_id]['question'] = request.form.get('question')
                faqs[faq_id]['description'] = request.form.get('description')
                
                # Save changes
                db['FAQs'] = faqs
                flash('FAQ updated successfully!', 'success')
                return redirect(url_for('faq'))
            else:
                flash('Only staff members can edit FAQs.', 'danger')
                return redirect(url_for('faq'))

        faq = faqs[faq_id] if faq_id < len(faqs) else None
        if faq:
            return render_template('edit_faq.html', faq=faq, faq_id=faq_id)
        else:
            flash('FAQ not found.', 'danger')
            return redirect(url_for('faq'))


def ensure_comments_key():
    db = get_db()
    faqs = db.get('FAQs', [])
    updated = False

    for faq in faqs:
        if 'comments' not in faq:
            faq['comments'] = []
            updated = True  # Mark that changes were made
        if 'description' not in faq:
            faq['description'] = None  # Ensure all existing FAQs have a 'description' key
            updated = True

    if updated:
        db['FAQs'] = faqs
        print("All FAQs now have a 'description' and 'comments' key.")
    db.close()


# aud codes
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total_price = sum(item.get('total_price', 0.0) for item in cart_items)  # Calculate total price
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    drink_name = request.form.get('drink_name')
    base_price = float(request.form.get('drink_price', 0))
    size = request.form.get('size', 'M')
    toppings = request.form.getlist('toppings')
    sugar_level = request.form.get('sugar_level', '100%')
    ice_level = request.form.get('ice_level', 'Normal')

    # Calculate total price with size adjustment and toppings (Tapioca Pearls are free)
    total_price = calculate_total_price(base_price, size, toppings)

    # Add item to cart
    cart_item = {
        'name': drink_name,
        'size': size,
        'sugar_level': sugar_level,
        'ice_level': ice_level,
        'toppings': toppings,
        'total_price': total_price
    }

    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(cart_item)
    session.modified = True

    flash('Drink added to cart!', 'success')
    return redirect(url_for('menu'))


def calculate_total_price(base_price, size, toppings):
    """Calculate the total price based on size and toppings."""
    size_adjustment = 1 if size == 'L' else 0  # Large adds $1
    topping_price = sum(0.50 for topping in toppings if topping != 'Tapioca Pearls')  # Only non-free toppings
    return base_price + size_adjustment + topping_price



@app.route('/remove_from_cart/<int:index>', methods=['POST'])
def remove_from_cart(index):
    if 'cart' in session and 0 <= index < len(session['cart']):
        del session['cart'][index]
        session.modified = True
        flash('Item removed from cart.', 'info')
    else:
        flash('Invalid item.', 'danger')
    return redirect(url_for('cart'))




#jiaens code
@app.route('/payment')
def payment():
    total_price = request.args.get('total_price', 0.0, type=float)  # Get total price from query parameters
    return render_template('payment.html', total_price=total_price)
@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Here you would handle the payment processing logic
    # For now, we will just redirect to the confirmation page with example data

    # Example data to pass to the confirmation page
    queue_number = random.randint(1, 100)  # Generate a random queue number
    order_time = datetime.now()
    estimated_pickup_time = order_time + timedelta(minutes=15)  # Estimated pickup time

    # Get cart items from session
    cart_items = session.get('cart', [])

    # Clear the cart after processing payment
    session.pop('cart', None)  # Clear the cart from the session

    # Redirect to confirmation page with data
    return render_template('confirmation.html', 
                           queue_number=queue_number, 
                           order_time=order_time.strftime('%Y-%m-%d %H:%M:%S'), 
                           estimated_pickup_time=estimated_pickup_time.strftime('%Y-%m-%d %H:%M:%S'),
                           cart_items=cart_items)  # Pass cart items to the confirmation page
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
