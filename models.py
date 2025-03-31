from datetime import datetime
from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    aadhar_card_no = db.Column(db.String(12), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __repr__(self):
        return f'<User {self.name}>'

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    aadhar_card_no = db.Column(db.String(12), nullable=False)
    phone_no = db.Column(db.String(15), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # New field for category
    rating = db.Column(db.Float, nullable=True, default=0)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __repr__(self):
        return f'<Vendor {self.name}>'

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(255))
    city = db.Column(db.String(100))
    category = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, default=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    photo = db.Column(db.String(150), nullable=True)  # New photo field
    schedule_date = db.Column(db.Date, nullable=True)
    schedule_time = db.Column(db.Time, nullable=True)

    user = db.relationship('User', backref=db.backref('complaints', lazy=True))
    vendor = db.relationship('Vendor', backref=db.backref('accepted_complaints', lazy=True))

    def __repr__(self):
        return f'<Complaint {self.description[:20]}...>'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Rent, Sell, Exchange
    price = db.Column(db.Float, nullable=False)
    photo = db.Column(db.String(100), nullable=True)  # Filepath to the product photo
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)

    

    user = db.relationship('User', backref=db.backref('products', lazy=True))
    vendor = db.relationship('Vendor', backref=db.backref('products', lazy=True))

    __table_args__ = (
        db.CheckConstraint(
            'user_id IS NOT NULL OR vendor_id IS NOT NULL',
            name='check_user_or_vendor'
        ),
        db.CheckConstraint(
            'user_id IS NULL OR vendor_id IS NULL',
            name='check_only_one_id'
        )
    )

    def __repr__(self):
        return f'<Product {self.name}>'



