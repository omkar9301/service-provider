from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from db import db
from models import User, Vendor, Complaint, Product
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///service_provider.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def home():
    return render_template('layout.html')

# User registration
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        date_of_birth_str = request.form['date_of_birth']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        pin_code = request.form['pin_code']
        aadhar_card_no = request.form['aadhar_card_no']
        phone_no = request.form['phone_no']

        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
            return redirect(url_for('register_user'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(
            name=name, email=email, password=hashed_password,
            date_of_birth=date_of_birth, city=city, state=state,
            address=address, pin_code=pin_code, aadhar_card_no=aadhar_card_no,
            phone_no=phone_no
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('register_user'))

        flash('User registered successfully!', 'success')
        return redirect(url_for('user_login'))

    return render_template('user_register.html')

@app.route('/register_vendor', methods=['GET', 'POST'])
def register_vendor():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        date_of_birth_str = request.form['date_of_birth']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        pin_code = request.form['pin_code']
        aadhar_card_no = request.form['aadhar_card_no']
        phone_no = request.form['phone_no']
        category = request.form['category']  # Capture the category

        # Convert date string to date object
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
            return redirect(url_for('register_vendor'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_vendor = Vendor(
            name=name, email=email, password=hashed_password,
            date_of_birth=date_of_birth, city=city, state=state,
            address=address, pin_code=pin_code, aadhar_card_no=aadhar_card_no,
            phone_no=phone_no, category=category  # Store the selected category
        )
        db.session.add(new_vendor)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
            return redirect(url_for('register_vendor'))

        flash('Vendor registered successfully!', 'success')
        return redirect(url_for('vendor_login'))

    return render_template('vendor_register.html')


# User login
@app.route('/login_user', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login failed. Check your email and/or password.', 'danger')

    return render_template('user_login.html')

# Vendor login
@app.route('/login_vendor', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        vendor = Vendor.query.filter_by(email=email).first()
        if vendor and check_password_hash(vendor.password, password):
            session['vendor_id'] = vendor.id
            flash('Login successful!', 'success')
            return redirect(url_for('vendor_dashboard'))
        else:
            flash('Login failed. Check your email and/or password.', 'danger')

    return render_template('vendor_login.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = db.session.get(User, session['user_id'])
    
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('user_login'))
    
    return render_template('user_dashboard.html', user=user)

@app.route('/vendor_dashboard')
def vendor_dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    
    vendor = db.session.get(Vendor, session['vendor_id'])
    
    if vendor is None:
        flash('Vendor not found.', 'danger')
        return redirect(url_for('vendor_login'))
    
    return render_template('vendor_dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('vendor_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('user_login'))
    
    user = db.session.get(User, session['user_id'])

    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('user_dashboard'))

    return render_template('user_profile.html', user=user)

@app.route('/vendor_profile')
def vendor_profile():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))
    vendor = Vendor.query.get(session['vendor_id'])
    return render_template('vendor_profile.html', vendor=vendor)


@app.route('/list_problem', methods=['GET', 'POST'])
def list_problem():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    # Fetch the user from the database using the session's user_id
    user = db.session.get(User, session['user_id'])

    # Pass the 'user' object to the template when rendering it
    return render_template('list_problem.html', user=user)

@app.route('/list_problem_1', methods=['GET', 'POST'])
def list_problem_1():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    # Fetch the user from the database using the session's user_id
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        description = request.form['description']
        category = request.form['category'].strip()
        city = request.form['city'].strip()

        photo = request.files.get('photo')
        photo_filename = None
        if photo and allowed_file(photo.filename):
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        new_complaint = Complaint(
            user_id=session['user_id'],
            description=description,
            category=category,
            city=city,
            photo=photo_filename
        )
        db.session.add(new_complaint)
        db.session.commit()

        flash('Complaint listed successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    # Pass the 'user' object to the template when rendering it
    return render_template('list_problem_1.html', user=user)

@app.route('/view_problems')
def view_problems():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))  # Redirect if vendor is not logged in

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    # Debugging: Print vendor details
    print(f"Vendor City: {vendor.city}, Category: {vendor.category}")

    try:
        # Fetch complaints based on vendor's city and category
        complaints = Complaint.query.filter_by(city=vendor.city.strip(), category=vendor.category.strip(), is_accepted=False).all()

        # Debugging: Print city and category for each complaint
        for complaint in complaints:
            print(f"Complaint City: {complaint.city}, Category: {complaint.category}")

    except Exception as e:
        print(f"An error occurred while fetching complaints: {e}")

    return render_template('view_problems.html', vendor=vendor, complaints=complaints)


@app.route('/accept_complaint/<int:complaint_id>', methods=['POST'])
def accept_complaint(complaint_id):
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    # Fetch the number of complaints the vendor has already accepted
    accepted_complaints_count = Complaint.query.filter_by(vendor_id=vendor_id).count()

    # Check if the vendor has reached the limit of 10 accepted complaints
    if accepted_complaints_count >= 10:
        flash('You have reached the limit of 10 accepted complaints.', 'danger')
        return redirect(url_for('view_problems'))

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('view_problems'))

    if complaint.vendor_id:
        flash('Complaint has already been accepted by another vendor.', 'danger')
        return redirect(url_for('view_problems'))

    # Proceed to accept the complaint if the limit has not been reached
    complaint.is_accepted = True
    complaint.vendor_id = vendor_id
    db.session.commit()

    flash('Complaint accepted successfully!', 'success')
    return redirect(url_for('accepted_work'))



@app.route('/accepted_work')
def accepted_work():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    # Fetch complaints accepted by the vendor
    complaints = Complaint.query.filter_by(vendor_id=vendor_id).all()
    
    for complaint in complaints:
        print(complaint.photo)

    return render_template('accepted_work.html', vendor=vendor, complaints=complaints)


@app.route('/view_complaint_details/<int:complaint_id>')
def view_complaint_details(complaint_id):
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return "Complaint not found", 404

    user = User.query.get(complaint.user_id)
    if not user:
        return "User not found", 404

    return render_template('complaint_details.html', complaint=complaint, user=user)


@app.route('/mark_work_solved/<int:complaint_id>', methods=['POST'])
def mark_work_solved(complaint_id):
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('accepted_work'))

    if complaint.vendor_id != vendor_id:
        flash('You cannot mark this complaint as solved.', 'danger')
        return redirect(url_for('accepted_work'))

    # Optionally, you can remove the complaint from the accepted list or mark it as solved
    db.session.delete(complaint)  # Remove or update the complaint as needed
    db.session.commit()
    flash('Complaint marked as solved.', 'success')
    return redirect(url_for('accepted_work'))

@app.route('/listed_complaints')
def listed_complaints():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))  # Redirect if user is not logged in

    user = db.session.get(User, session['user_id'])

    if not user:
        return "User not found", 404

    # Fetch complaints that are not accepted yet
    complaints = Complaint.query.filter_by(is_accepted=False, user_id=user_id).all()

    # Pass both `user` and `complaints` to the template
    return render_template('listed_complaints.html', user=user, complaints=complaints)


@app.route('/accepted_complaints')
def accepted_complaints():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_user'))  # Redirect if user is not logged in

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    # Fetch complaints accepted by the user
    complaints = Complaint.query.filter_by(user_id=user_id, is_accepted=True).all()

    # Debugging: Print user details and complaints
    print(f"User ID: {user_id}")
    print(f"Accepted Complaints: {[complaint.id for complaint in complaints]}")

    return render_template('accepted_complaints.html', complaints=complaints, user=user)



@app.route('/view_vendor_details/<int:vendor_id>')
def view_vendor_details(vendor_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = db.session.get(User, session['user_id'])

    if not user:
        return "User not found", 404

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    return render_template('vendor_details.html', vendor=vendor)

@app.route('/view_vendor_details2/<int:vendor_id>')
def view_vendor_details2(vendor_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    
    user = db.session.get(User, session['user_id'])

    if not user:
        return "User not found", 404

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    return render_template('vendor_details2.html', vendor=vendor)

@app.route('/rate_vendor/<int:vendor_id>', methods=['POST'])
def rate_vendor(vendor_id):
    if 'user_id' not in session:
        return redirect(url_for('user_login'))

    user = db.session.get(User, session['user_id'])

    if not user:
        return "User not found", 404

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    # Get the rating from the form
    rating = request.form.get('rating')
    try:
        rating = float(rating)
        if rating < 1 or rating > 5:
            flash("Please enter a rating between 1 and 5.", "danger")
            return redirect(url_for('view_vendor_details', vendor_id=vendor.id))

        # Update vendor's rating
        if vendor.rating:
            vendor.rating = (vendor.rating + rating) / 2  # Average rating
        else:
            vendor.rating = rating

        db.session.commit()

        flash("Rating submitted successfully.", "success")
        return redirect(url_for('view_vendor_details', vendor_id=vendor.id))

    except ValueError:
        flash("Invalid rating value.", "danger")
        return redirect(url_for('view_vendor_details', vendor_id=vendor.id))


# Assuming you have a db.session or similar session object
@app.route('/view_user_details/<int:user_id>')
def view_user_details(user_id):
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))

    vendor = db.session.get(Vendor, session['vendor_id'])
    if not vendor:
        return "Vendor not found", 404

    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 404

    return render_template('user_details.html', user=user)

# Similarly, update other routes using the deprecated method


@app.route('/update_user_profile', methods=['POST'])
def update_user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    user.lat = request.form['lat']
    user.lng = request.form['lng']
    # Update other user details as needed
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('user_profile'))

@app.route('/update_vendor_profile', methods=['POST'])
def update_vendor_profile():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return "Vendor not found", 404

    vendor.lat = request.form['lat']
    vendor.lng = request.form['lng']
    # Update other vendor details as needed
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('vendor_profile'))

@app.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    user_id = data.get('user_id')
    vendor_id = data.get('vendor_id')
    lat = data.get('lat')
    lng = data.get('lng')

    user = User.query.get(user_id)
    vendor = Vendor.query.get(vendor_id)
    if user:
        user.lat = lat
        user.lng = lng
        db.session.commit()
        return jsonify({'status': 'success'})
    elif vendor:
        vendor.lat = lat
        vendor.lng = lng
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'User not found'})


@app.route('/list_product', methods=['GET', 'POST'])
def list_product():
    user_id = session.get('user_id')
    vendor_id = session.get('vendor_id')

    # Handle GET request and render the appropriate template based on login
    if request.method == 'GET':
        if user_id:
            user = db.session.get(User, session['user_id'])
            if not user:
                return "User not found", 404
            return render_template('list_product_user.html', user=user)
        elif vendor_id:
            vendor = Vendor.query.get(vendor_id)
            if not vendor:
                return "Vendor not found", 404
            return render_template('list_product_vendor.html', vendor=vendor)
        else:
            return redirect(url_for('login'))  # Redirect to login if not logged in

    # Handle POST request for form submission
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        # Handle file upload
        photo = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                photo = filename

        # Ensure only one of user_id or vendor_id is set
        if user_id and vendor_id:
            return "Error: Cannot be associated with both a user and a vendor", 400
        elif not user_id and not vendor_id:
            return "Error: Must be associated with either a user or a vendor", 400

        # Create new product
        new_product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            photo=photo,
            user_id=user_id,
            vendor_id=vendor_id
        )

        try:
            db.session.add(new_product)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return "Error: Could not add the product", 500

        return redirect(url_for('browse_products'))


@app.route('/browse_products')
def browse_products():
    # Check if the user or vendor is logged in
    user_id = session.get('user_id')
    vendor_id = session.get('vendor_id')

    if user_id:
        user = User.query.get(user_id)
        if not user:
            return "User not found", 404
    elif vendor_id:
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return "Vendor not found", 404
    else:
        return redirect(url_for('login_user'))  # Redirect to login if neither is logged in

    # Get filter parameters
    name = request.args.get('name')
    category = request.args.get('category', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', float('inf'), type=float)

    # Apply filters to product query
    query = Product.query
    if name:
        query = query.filter(Product.name.ilike(f'%{name}%'))
    if category:
        query = query.filter(Product.category.ilike(f'%{category}%'))
    if min_price:
        query = query.filter(Product.price >= float(min_price))
    if max_price:
        query = query.filter(Product.price <= float(max_price))

    products = query.all()

    # Render the appropriate template based on user type
    if user_id:
        return render_template('browse_products_user.html', products=products, user=user)
    else:
        return render_template('browse_products_vendor.html', products=products, vendor=vendor)

@app.route('/vendors')
def vendors_list():
    # Fetch all vendors from the database
    vendors = Vendor.query.all()  
    return render_template('vendors_list.html', vendors=vendors)

@app.route('/history')
def history():
    if 'vendor_id' not in session:
        return redirect(url_for('vendor_login'))

    vendor = db.session.get(Vendor, session['vendor_id'])

    if not vendor:
        return "User not found", 404

    # Query accepted complaints
    accepted_complaints = Complaint.query.filter_by(is_accepted=True).all()

    return render_template('history.html', complaints=accepted_complaints)

@app.route('/database')
def database():
    # Fetching data from each table
    users = User.query.all()
    vendors = Vendor.query.all()
    complaints = Complaint.query.all()
    products = Product.query.all()
    
    # Rendering the template with the fetched data
    return render_template('database.html', users=users, vendors=vendors, complaints=complaints, products=products)


with app.app_context():
    print(app.url_map)


if __name__ == '__main__':
    app.run(debug=True)
