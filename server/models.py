from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# Association Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'customer', 'staff', 'admin'

    customer = db.relationship('Customer', backref='user', uselist=False)
    staff = db.relationship('Staff', backref='user', uselist=False)
    admin = db.relationship('Admin', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

# Role-based profiles

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    savings_account = db.relationship('SavingsAccount', uselist=False, back_populates='customer')
    loans = db.relationship('Loan', backref='customer', lazy=True)


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

     # Enforce a single row via a check constraint (PostgreSQL-specific)
    __table_args__ = (
        db.CheckConstraint('id = 1', name='only_one_admin'),
    )

# Savings Account

class SavingsAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), unique=True)

    customer = db.relationship('Customer', back_populates='savings_account')

# Loans

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    loan_duration = db.Column(db.Integer, nullable=False)  # in months
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, repaid
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    def approve_loan(self,user):
        if user.role not in ['admin', 'staff']:
            raise PermissionError("Only admins or staff can approve loans.")
        self.status = 'approved'

    def reject_loan(self,user):
        if user.role not in ['admin', 'staff']:
            raise PermissionError("Only admins or staff can approve loans.")
        self.status = 'rejected'

    def add_repayment(self, customer, amount, method=None, ref=None):
        if self.customer_id != customer.id:
            raise PermissionError("This customer does not own the loan.")
        if self.status != 'approved':
            raise ValueError("Cannot repay a loan that is not approved.")

        repayment = Repayment(
            loan=self,
            customer=customer,
            amount=amount,
            payment_method=method,
            reference=ref
        )
        db.session.add(repayment)

        total_repaid = sum(r.amount for r in self.repayments) + amount
        total_due = self.amount * (1 + self.interest_rate / 100)

        if total_repaid >= total_due:
            self.status = 'repaid'

        db.session.commit()
        return repayment

# Loan settings (editable by Admin only)

class LoanSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    default_interest_rate = db.Column(db.Float, nullable=False)




class Repayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)

    # Optional: who made the payment
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer')

    # Optional: transaction reference or method (bank, transfer, etc.)
    payment_method = db.Column(db.String(50))
    reference = db.Column(db.String(100))
