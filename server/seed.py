from app import app
from models import db, User, Loan, Customer, Staff, Admin
from werkzeug.security import generate_password_hash

# Creating some sample users and loan data
def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create Admin User
        admin = User(username="adminuser", email="admin@example.com", role="admin")
        admin.set_password("admin1234")
        db.session.add(admin)
        db.session.commit()

        # Create Admin Profile
        admin_profile = Admin(user=admin, access_level="full", is_superuser=True)
        db.session.add(admin_profile)
        db.session.commit()

        # Create Staff User
        staff = User(username="staffuser", email="staff@example.com", role="staff")
        staff.set_password("staff1234")
        db.session.add(staff)
        db.session.commit()

        # Create Staff Profile
        staff_profile = Staff(user=staff, employee_id="S001", department="Loans")
        db.session.add(staff_profile)
        db.session.commit()

        # Create Customer Users with Loans
        customer_1 = User(username="customer1", email="customer1@example.com", role="customer")
        customer_1.set_password("customer1234")
        db.session.add(customer_1)
        db.session.commit()

        # Create Customer Profile for Customer 1
        customer_profile_1 = Customer(user=customer_1, account_number="C001", address="123 Main St", national_id="1234567890")
        db.session.add(customer_profile_1)
        db.session.commit()

        # Create Loans for Customer 1
        loan_1 = Loan(amount=5000, interest_rate=5.5, loan_duration=12, customer_id=customer_1.id)
        db.session.add(loan_1)

        customer_2 = User(username="customer2", email="customer2@example.com", role="customer")
        customer_2.set_password("customer1234")
        db.session.add(customer_2)
        db.session.commit()

        # Create Customer Profile for Customer 2
        customer_profile_2 = Customer(user=customer_2, account_number="C002", address="456 Elm St", national_id="9876543210")
        db.session.add(customer_profile_2)
        db.session.commit()

        # Create Loans for Customer 2
        loan_2 = Loan(amount=10000, interest_rate=6.0, loan_duration=24, customer_id=customer_2.id)
        db.session.add(loan_2)

        # Commit all data to the database
        db.session.commit()

        print("Database seeded successfully.")

if __name__ == "__main__":
    seed_data()
