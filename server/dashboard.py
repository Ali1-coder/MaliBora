from flask_restful import Resource
from flask import jsonify
from flask_login import login_required, current_user
from models import Customer, Staff, Admin

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
