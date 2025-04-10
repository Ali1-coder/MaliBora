from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import db, User, Customer, Staff, Admin, Loan, LoanSettings, SavingsAccount, Transaction
from werkzeug.security import check_password_hash
from sqlalchemy.orm.exc import NoResultFound
from flask_migrate import Migrate
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
api = Api(app)
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


# -----------------------------------------------------
# ADMIN-ONLY User Creation (Registration is Admin Controlled)
# -----------------------------------------------------
class AdminCreateUserResource(Resource):
    @admin_required
    def post(self):
        data = request.get_json()

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')  # Expected: 'customer', 'staff', (or 'admin' if desired)

        if role not in ['customer', 'staff', 'admin']:
            return {'error': 'Invalid role'}, 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return {'error': 'Username or Email already exists'}, 400

        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Create the corresponding role-based profile
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

        return {'message': f'{role.capitalize()} created successfully!'}, 201


# -----------------------------------------------------
# Login & Logout
# -----------------------------------------------------
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

class DashboardResource(Resource):
    @login_required
    def get(self):
        if current_user.role == 'customer':
            profile = current_user.customer_profile
            return jsonify({
                'message': f'Welcome {current_user.username}!',
                'account_number': profile.account_number,
                'address': profile.address,
                'national_id': profile.national_id
            })
        elif current_user.role == 'staff':
            profile = current_user.staff_profile
            return jsonify({
                'message': f'Welcome {current_user.username}!',
                'employee_id': profile.employee_id,
                'department': profile.department
            })
        elif current_user.role == 'admin':
            profile = current_user.admin_profile
            return jsonify({
                'message': f'Welcome {current_user.username}!',
                'access_level': profile.access_level,
                'is_superuser': profile.is_superuser
            })
        else:
            return jsonify({'error': 'Unauthorized'}), 403

class Logout(Resource):
    def get(self):
        if current_user.is_authenticated:
            logout_user()
            return {'message': 'Logged out successfully!'}, 200
        return {'error': 'No user logged in'}, 400


# -----------------------------------------------------
# User Management for Admins
# -----------------------------------------------------
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
        if user.role == 'admin':  # Prevent deletion of admin accounts
            return {'error': 'Cannot delete an admin user'}, 400
        
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User {user_id} deleted successfully'}, 200


# -----------------------------------------------------
# Loan Endpoints (Application, Status, Management)
# -----------------------------------------------------
class LoanApply(Resource):
    @customer_required
    def post(self):
        data = request.get_json()
        amount = data.get('amount')
        loan_duration = data.get('loan_duration')

        if not all([amount, loan_duration]):
            return {'error': 'Missing loan details'}, 400
        
        if amount <= 0 or loan_duration <= 0:
            return {'error': 'Invalid loan details'}, 400

        settings = LoanSettings.query.first()
        if not settings:
            return {'error': 'Interest rate configuration missing. Contact admin.'}, 500
        interest_rate = settings.default_interest_rate

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
        loan = Loan.query.filter_by(id=loan_id, customer_id=current_user.id).first_or_404()
        return jsonify({
            'loan_id': loan.id,
            'amount': loan.amount,
            'status': loan.status,
            'interest_rate': loan.interest_rate,
            'loan_duration': loan.loan_duration
        })


class LoanManagement(Resource):
    def put(self, loan_id):
        # Only staff or admin can approve/reject loans
        if current_user.role not in ['staff', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()
        status = data.get('status')  # Expected: 'approved' or 'rejected'
        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400

        loan = Loan.query.get_or_404(loan_id)
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


# -----------------------------------------------------
# Savings and Loan Repayment Endpoints
# -----------------------------------------------------
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


class RepayLoanResource(Resource):
    @login_required
    def post(self):
        if current_user.role != 'customer':
            return jsonify({"error": "Only customers can make repayments"}), 403

        parser = reqparse.RequestParser()
        parser.add_argument('loan_id', type=int, required=True, help='Loan ID is required')
        parser.add_argument('amount', type=float, required=True, help='Amount is required')
        parser.add_argument('payment_method', type=str, help='Payment method (optional)')
        parser.add_argument('reference', type=str, help='Payment reference (optional)')
        args = parser.parse_args()

        loan_id = args['loan_id']
        amount = args['amount']
        method = args['payment_method']
        reference = args['reference']

        customer = current_user.customer
        if not customer:
            return jsonify({"error": "User has no customer profile"}), 404

        loan = Loan.query.filter_by(id=loan_id).first()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404

        if loan.customer_id != customer.id:
            return jsonify({"error": "You do not own this loan"}), 403

        try:
            repayment = loan.add_repayment(
                customer=customer,
                amount=amount,
                method=method,
                ref=reference
            )
            total_repaid = sum(r.amount for r in loan.repayments)
            return jsonify({
                "message": "Repayment successful",
                "repayment_id": repayment.id,
                "loan_status": loan.status,
                "total_repaid": total_repaid
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400


class LoanRepaymentsResource(Resource):
    def get(self, loan_id):
        loan = Loan.query.filter_by(id=loan_id).first()
        if not loan:
            return jsonify({"error": "Loan not found"}), 404

        repayments = [{
            "amount": r.amount,
            "payment_date": r.payment_date,
            "method": r.payment_method,
            "reference": r.reference
        } for r in loan.repayments]

        return jsonify({
            "loan_id": loan.id,
            "repayments": repayments
        })


# -----------------------------------------------------
# Deposit and Withdrawal Endpoints using Transaction Model
# -----------------------------------------------------
class DepositResource(Resource):
    @login_required
    def post(self):
        if current_user.role != 'customer':
            return jsonify({"error": "Only customers can make deposits"}), 403

        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help="Amount is required")
        parser.add_argument('reference', type=str, help="Transaction reference (optional)")
        args = parser.parse_args()

        customer = current_user.customer
        savings_account = customer.savings_account
        if not savings_account:
            return jsonify({"error": "Customer does not have a savings account"}), 404

        try:
            transaction = savings_account.deposit(args['amount'], args['reference'])
            return jsonify({
                "message": "Deposit successful",
                "transaction_id": transaction.id,
                "balance": savings_account.balance
            }), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


class WithdrawResource(Resource):
    @login_required
    def post(self):
        if current_user.role != 'customer':
            return jsonify({"error": "Only customers can make withdrawals"}), 403

        parser = reqparse.RequestParser()
        parser.add_argument('amount', type=float, required=True, help="Amount is required")
        parser.add_argument('reference', type=str, help="Transaction reference (optional)")
        args = parser.parse_args()

        customer = current_user.customer
        savings_account = customer.savings_account
        if not savings_account:
            return jsonify({"error": "Customer does not have a savings account"}), 404

        try:
            transaction = savings_account.withdraw(args['amount'], args['reference'])
            return jsonify({
                "message": "Withdrawal successful",
                "transaction_id": transaction.id,
                "balance": savings_account.balance
            }), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400


# -----------------------------------------------------
# Admin Approval/Rejection for Withdrawal Transactions
# -----------------------------------------------------
class AdminApproveRejectTransactionResource(Resource):
    @login_required
    def put(self, transaction_id, action):
        if current_user.role != 'admin':
            return jsonify({"error": "Only admins can approve/reject transactions"}), 403

        if action not in ['approve', 'reject']:
            return jsonify({"error": "Invalid action. Choose 'approve' or 'reject'."}), 400

        transaction = Transaction.query.filter_by(id=transaction_id, transaction_type='withdrawal').first()
        if not transaction:
            return jsonify({"error": "Transaction not found or not a withdrawal"}), 404
        
        if transaction.status != 'pending':
            return jsonify({"error": "This transaction has already been processed"}), 400

        try:
            if action == 'approve':
                transaction.approve()
            elif action == 'reject':
                transaction.reject()
            
            db.session.commit()
            return jsonify({
                "message": f"Withdrawal transaction {action}d successfully",
                "transaction_id": transaction.id,
                "new_status": transaction.status
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


# -----------------------------------------------------
# Register Resources with API
# -----------------------------------------------------
api.add_resource(AdminCreateUserResource, '/api/admin/create-user')
api.add_resource(Login, '/api/login')
api.add_resource(Logout, '/api/logout')
api.add_resource(DashboardResource, '/api/dashboard')
api.add_resource(LoanApply, '/api/loan/apply')
api.add_resource(LoanStatus, '/api/loan/<int:loan_id>')
api.add_resource(LoanManagement, '/api/loan/<int:loan_id>/manage')
api.add_resource(UserManagement, '/api/user/<int:user_id>')
api.add_resource(LoanSettingsResource, '/api/admin/loan-settings')
api.add_resource(RepayLoanResource, '/repay-loan')
api.add_resource(LoanRepaymentsResource, '/loan/<int:loan_id>/repayments')
api.add_resource(DepositResource, '/deposit')
api.add_resource(WithdrawResource, '/withdraw')
api.add_resource(AdminApproveRejectTransactionResource, '/admin/withdrawal-transaction/<int:transaction_id>/<string:action>')

if __name__ == '__main__':
    app.run(debug=True)
