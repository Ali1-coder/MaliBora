from app import app, db
from models import User, Customer, Staff, Admin, SavingsAccount, LoanSettings, Loan, Transaction
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Create Users ---
        admin_user = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            password_hash=generate_password_hash('adminpass')
        )

        staff_user = User(
            username='staff',
            email='staff@example.com',
            role='staff',
            password_hash=generate_password_hash('staffpass')
        )

        customer_user = User(
            username='customer',
            email='customer@example.com',
            role='customer',
            password_hash=generate_password_hash('customerpass')
        )

        db.session.add_all([admin_user, staff_user, customer_user])
        db.session.commit()

        # --- Role Profiles ---
        admin_profile = Admin(user=admin_user)
        staff_profile = Staff(user=staff_user)
        customer_profile = Customer(user=customer_user)

        db.session.add_all([admin_profile, staff_profile, customer_profile])
        db.session.commit()

        # --- Savings Account ---
        savings_account = SavingsAccount(customer=customer_profile, balance=1000.0)
        db.session.add(savings_account)
        db.session.commit()

        # --- Deposit and Withdrawal Transactions ---
        deposit = Transaction(
            amount=300.0,
            transaction_type='deposit',
            status='approved',
            customer=customer_profile,
            reference='Seed Deposit'
        )
        withdrawal = Transaction(
            amount=100.0,
            transaction_type='withdrawal',
            status='approved',
            customer=customer_profile,
            reference='Seed Withdrawal'
        )
        db.session.add_all([deposit, withdrawal])
        db.session.commit()

        # --- Loan Settings ---
        loan_settings = LoanSettings(default_interest_rate=5.0)
        db.session.add(loan_settings)
        db.session.commit()

        # --- Loan for Customer ---
        loan = Loan(
            amount=500.0,
            interest_rate=loan_settings.default_interest_rate,
            loan_duration=6,
            status='approved',
            customer_id=customer_profile.id
        )
        db.session.add(loan)
        db.session.commit()

        print("🌱 Database seeded successfully!")

if __name__ == '__main__':
    seed()
