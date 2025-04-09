from flask import Flask,request, jsonify
from flask_restful import Api,Resource 
from flask_login import LoginManager,login_user, logout_user, current_user

from models import db, User, Customer, Staff, Admin,Loan,LoanSettings,SavingsAccount
from werkzeug.security import check_password_hash

from sqlalchemy.orm.exc import NoResultFound


from dashboard import DashboardResource
from flask_migrate import Migrate

from functools import wraps




app = Flask(__name__)
api=Api(app)
app.config['SECRET_KEY'] = 'a9b7f8cbe34d4fd28b239872c88f199e'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def login_required_resource(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        return func(*args, **kwargs)
    return wrapper

def customer_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        if current_user.role != 'customer':
            return {'error': 'Access denied: customers only'}, 403
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        if current_user.role != 'admin':
            return {'error': 'Access denied: admin only'}, 403
        return func(*args, **kwargs)
    return wrapper
class Register(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')  # 'customer', 'staff', or 'admin'
        
        if role not in ['customer', 'staff', 'admin']:
            return {'error': 'Invalid role'}, 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return {'error': 'Username or Email already exists'}, 400
        
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Create profile based on role
        if role == 'customer':
            customer = Customer(user=new_user)
            db.session.add(customer)
            savings = SavingsAccount(customer=customer, balance=0.0)
            db.session.add(savings)
        elif role == 'staff':
            db.session.add(Staff(user=new_user))
        elif role == 'admin':
            db.session.add(Admin(user=new_user))

       
        db.session.commit()

        return {'message': 'User created successfully!'}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return {'message': f'Logged in as {user.username}'}, 200
        return {'error': 'Invalid credentials'}, 401


class Logout(Resource):
    def get(self):
        if current_user.is_authenticated:
            logout_user()
            return {'message': 'Logged out successfully!'}, 200
        return {'error': 'No user logged in'}, 400
    

class UserManagement(Resource):
    @admin_required
    def put(self, user_id):
        data = request.get_json()
        new_role = data.get('role')  # Example: updating a user's role

        if new_role not in ['customer', 'staff', 'admin']:
            return {'error': 'Invalid role'}, 400

        user = User.query.get_or_404(user_id)
        user.role = new_role  # Update the user's role
        db.session.commit()

        return {'message': f'User {user_id} updated to {new_role} role'}, 200

    @admin_required
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        
        # Prevent deletion of the admin user (if you want to protect yourself from accidental deletion)
        if user.role == 'admin':
            return {'error': 'Cannot delete an admin user'}, 400
        
        db.session.delete(user)
        db.session.commit()

        return {'message': f'User {user_id} deleted successfully'}, 200

class LoanApply(Resource):
    @customer_required
    def post(self):
        data = request.get_json()
        
        amount = data.get('amount')
        loan_duration = data.get('loan_duration')
        

        if not all([amount,loan_duration]):
            return {'error': 'Missing loan details'}, 400
        
        if amount <= 0 or interest_rate <= 0 or loan_duration <= 0:
            return {'error': 'Invalid loan details'}, 400
        
        # Get default interest rate from settings
        settings = LoanSettings.query.first()
        if not settings:
            return {'error': 'Interest rate configuration missing. Contact admin.'}, 500
        
        interest_rate = settings.default_interest_rate

        # Create loan entry for customer
        new_loan = Loan(
            amount=amount,
            interest_rate=interest_rate,
            loan_duration=loan_duration,
            customer_id=current_user.id
        )
        db.session.add(new_loan)
        db.session.commit()

        return {'message': 'Loan application submitted successfully!'}, 201


class LoanStatus(Resource):
    def get(self, loan_id):
        try:
            loan = Loan.query.filter_by(id=loan_id, customer_id=current_user.id).first_or_404()

            return jsonify({
                'loan_id': loan.id,
                'amount': loan.amount,
                'status': loan.status,
                'interest_rate': loan.interest_rate,
                'loan_duration': loan.loan_duration
            })
        except NoResultFound:
            return jsonify({'error': 'Loan not found or you do not have access to this loan'}), 404


class LoanManagement(Resource):
    def put(self, loan_id):
        # Only staff or admin can approve/reject loans
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        status = data.get('status')  # 'approved' or 'rejected'

        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400

        # Get the loan by ID
        loan = Loan.query.get_or_404(loan_id)

        # Update loan status based on approval/rejection
        if status == 'approved':
            loan.approve_loan()
        else:
            loan.reject_loan()

        db.session.commit()

        return jsonify({'message': f'Loan {status} successfully'}), 200
    
class LoanSettingsResource(Resource):
    @admin_required
    def put(self):
        data = request.get_json()
        new_rate = data.get('interest_rate')

        if not new_rate or new_rate <= 0:
            return {'error': 'Invalid interest rate'}, 400

        settings = LoanSettings.query.first()
        if not settings:
            settings = LoanSettings(default_interest_rate=new_rate)
            db.session.add(settings)
        else:
            settings.default_interest_rate = new_rate
        
        db.session.commit()

        return {'message': f'Default interest rate updated to {new_rate}%'}, 200
    
class Savings(Resource):
    @customer_required
    def get(self):
        savings = current_user.customer.savings_account
        return {'balance': savings.balance}, 200

    @customer_required
    def post(self):
        data = request.get_json()
        amount = data.get('amount')
        action = data.get('action')  # 'deposit' or 'withdraw'

        if not amount or amount <= 0 or action not in ['deposit', 'withdraw']:
            return {'error': 'Invalid request'}, 400

        savings = current_user.customer.savings_account

        if action == 'deposit':
            savings.balance += amount
        elif action == 'withdraw':
            if savings.balance < amount:
                return {'error': 'Insufficient funds'}, 400
            savings.balance -= amount

        db.session.commit()
        return {'message': f'{action.capitalize()} successful', 'new_balance': savings.balance}, 200
    
class LoanRepayment(Resource):
    @customer_required
    def post(self, loan_id):
        data = request.get_json()
        amount = data.get('amount')

        if not amount or amount <= 0:
            return {'error': 'Invalid repayment amount'}, 400

        loan = Loan.query.filter_by(id=loan_id, customer_id=current_user.id).first_or_404()

        if loan.status != 'approved':
            return {'error': 'Loan is not in a repayable state'}, 400

        savings = current_user.customer.savings_account

        if savings.balance < amount:
            return {'error': 'Insufficient savings to repay loan'}, 400

        savings.balance -= amount
        loan.amount -= amount

        if loan.amount <= 0:
            loan.status = 'repaid'
            loan.amount = 0.0

        db.session.commit()

        return {'message': 'Loan repayment successful', 'remaining_loan_amount': loan.amount}, 200




# Add resources to API
api.add_resource(Register, '/api/register')
api.add_resource(Login, '/api/login')
api.add_resource(Logout, '/api/logout')
api.add_resource(DashboardResource, '/api/dashboard')
api.add_resource(LoanApply, '/api/loan/apply')  # Loan application route
api.add_resource(LoanStatus, '/api/loan/<int:loan_id>')  # View loan status
api.add_resource(LoanManagement, '/api/loan/<int:loan_id>/manage')  # Staff/Admin loan approval
api.add_resource(UserManagement, '/api/user/<int:user_id>')
api.add_resource(LoanSettingsResource, '/api/admin/loan-settings')
api.add_resource(Savings, '/api/savings')  # GET balance, POST deposit/withdraw
api.add_resource(LoanRepayment, '/api/loan/<int:loan_id>/repay')  # POST


if __name__ == '__main__':
    app.run(debug=True)
