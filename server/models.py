from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)





class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer', 'staff', 'admin'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    account_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    national_id = db.Column(db.String(30))

    
    
    savings_account = db.relationship('SavingsAccount', uselist=False, back_populates='customer')
    loans = db.relationship('Loan', backref='customer', lazy=True)


    user = db.relationship('User', backref=db.backref('customer', uselist=False))


class Staff(db.Model):
    __tablename__ = 'staffs'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    employee_id = db.Column(db.String(30))
    department = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('staff', uselist=False))


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    access_level = db.Column(db.String(30))
    is_superuser = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('admin', uselist=False))

class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    interest_rate = db.Column(db.Float, nullable=False)
    loan_duration = db.Column(db.Integer, nullable=False)  # Duration in months
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer = db.relationship('User', backref=db.backref('loans', lazy=True))

    def approve_loan(self):
        self.status = 'approved'

    def reject_loan(self):
        self.status = 'rejected'

class LoanSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    default_interest_rate = db.Column(db.Float, nullable=False)


class SavingsAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), unique=True)
    
    customer = db.relationship('Customer', back_populates='savings_account')
