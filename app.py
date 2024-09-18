
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
from urllib.parse import quote_plus
import re 


app = Flask(__name__)
pwd = quote_plus('nitin@123')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{pwd}@localhost/irctc' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'qh7lTK7rDzbV7mz5xVpF6Q'  
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['ADMIN_API_KEY'] = 'rFy-3xnIPSgkpyFArXjZlQ'  

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user'), default='user')

class Train(db.Model):
    __tablename__ = 'trains'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)

def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user and user.role == 'admin':
            return fn(*args, **kwargs)
        return jsonify({"msg": "Admin access required"}), 403
    return wrapper

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, email)



@app.route('/')
def home():
    return "Welcome to IRCTC API"


# Register a User
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not is_valid_email(data['email']):
        return jsonify({"msg": "Invalid email format."}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"msg": "Email already registered."}), 400
    

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=data.get('role', 'user') 
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e :
        return jsonify({"msg": e}), 500




#. Login User
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not is_valid_email(data['email']):
        return jsonify({"msg": "Invalid email format."}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, role=user.role), 200
    return jsonify({"msg": "Invalid email or password"}), 401





#  Add a New Train
@app.route('/train', methods=['POST'])
@jwt_required()
def add_train():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.role != 'admin':
        return jsonify({"msg": "Admin access required"}), 403

    data = request.get_json()
    new_train = Train(
        name=data['name'],
        source=data['source'],
        destination=data['destination'],
        total_seats=data['total_seats']
    )

    try:
        db.session.add(new_train)
        db.session.commit()
        return jsonify({"msg": "Train added successfully"}), 201
    except Exception as e:
        return jsonify({"msg": e}), 500
    



#  Get Seat Availability
@app.route('/availability', methods=['POST'])
def get_availability():

    data = request.get_json()
    source = data['source']
    destination = data['destination']

    if not source or not destination:
        return jsonify({"msg": "Source and destination are required."}), 400
    

    trains = Train.query.filter_by(source=source, destination=destination).all()

    if not trains:
            return jsonify({"msg": "No trains found for the given source and destination."}), 404
    

    result = []

    for train in trains:
        booked_seats = db.session.query(db.func.sum(Booking.seats_booked)).filter_by(train_id=train.id).scalar() or 0
        # available_seats = train.total_seats - booked_seats
        result.append({
            "id": train.id,
            "name": train.name,
            "available_seats": train.total_seats,
            "source": train.source,  
            "destination": train.destination  
        })
    return jsonify(result), 200


 # Book a Seat
@app.route('/book', methods=['POST'])
@jwt_required()
def book_seat():
    data = request.get_json()
    user_id = get_jwt_identity()
    train = Train.query.get(data['train_id'])
    
    if not train:
        return jsonify({"msg": "Train not found"}), 404
    
    booked_seats = db.session.query(db.func.sum(Booking.seats_booked)).filter_by(train_id=train.id).scalar() or 0
    available_seats = train.total_seats - booked_seats
    
    if available_seats < data['seats']:
        return jsonify({"msg": "Not enough seats available"}), 400
    
    try:
        new_booking = Booking(user_id=user_id, train_id=data['train_id'], seats_booked=data['seats'])
        db.session.add(new_booking)
        train.total_seats -= data['seats']

        db.session.commit()
        return jsonify({"msg": "Booking successful", "booking_id": new_booking.id}), 201
    
    except Exception as e:
        return jsonify({"msg": e}), 500


#  Get Specific Booking Details
@app.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        return jsonify({"msg": "Booking not found"}), 404
    train = Train.query.get(booking.train_id)
    return jsonify({
        "booking_id": booking.id,
        "train_name": train.name,
        "seats_booked": booking.seats_booked,
        "source": train.source,
        "destination": train.destination
    }), 200

if __name__ == '__main__':
    app.run(debug=True)