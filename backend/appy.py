from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Enable CORS to allow frontend to access backend

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    referral_code = db.Column(db.String(6), unique=True, nullable=False)
    referrals = db.Column(db.PickleType, default=[])
    balance = db.Column(db.Float, default=0.0)  # Import the User model

# Route to register a new user
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    phone_number = data.get('phone_number')

    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    new_user = User(username=username, email=email, phone_number=phone_number, referral_code=referral_code)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'referral_code': referral_code}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Route to handle referrals
@app.route('/api/referral', methods=['POST'])
def handle_referral():
    data = request.get_json()
    referral_code = data.get('referral_code')
    new_user_id = data.get('new_user_id')

    referrer = User.query.filter_by(referral_code=referral_code).first()
    new_user = User.query.get(new_user_id)

    if referrer and new_user:
        referrer.referrals.append(new_user.id)
        referrer.balance += 10  # For example, referrer gets 10 KSH for each successful referral
        db.session.commit()
        return jsonify({'message': 'Referral added successfully'})
    
    return jsonify({'message': 'Invalid referral code or user not found'}), 400

if __name__ == '__main__':
    db.create_all()  # Create tables if they do not exist
    app.run(debug=True)
