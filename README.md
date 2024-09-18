# IRCTC API

 This API allows users to manage train bookings, including user registration, login, train management, seat availability checking, and booking seats. It is built using Flask, SQLAlchemy, and JWT for authentication.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
  - [Home](#home)
  - [User Registration](#user-registration)
  - [User Login](#user-login)
  - [Add Train](#add-train)
  - [Check Seat Availability](#check-seat-availability)
  - [Book a Seat](#book-a-seat)
  - [Get Booking Details](#get-booking-details)
- [Running the Application](#running-the-application)

## Features

- User registration and login.
- Admin-only endpoint to add new trains.
- Check seat availability for trains.
- Book seats on a specific train.
- Retrieve booking details for a user.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework for Python.
- **Flask-SQLAlchemy**: An ORM that simplifies database interactions.
- **Flask-JWT-Extended**: A library for creating and managing JSON Web Tokens.
- **Werkzeug**: A library for secure password hashing.

## Installation

To run this API, you need Python 3.6 or higher. Follow these steps:

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd irctc-api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```bash
   pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Werkzeug
   ```

4. **Set up the database** (use SQLite for simplicity):
   Update the database URI in the code:
   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{pwd}@{host}/{db}'
   ```

## Configuration

Before running the application, you may need to configure the following in your application:

- **Secret Key**: Set a secret key for JWT encoding/decoding.
   ```python
   app.config['JWT_SECRET_KEY'] = 'your_secret_key'
   app.config['ADMIN_API_KEY'] = 'admin_api_key'
   ```

## API Endpoints

### Home
- **Endpoint**: `GET /`
- **Description**: Welcome message.

### User Registration
- **Endpoint**: `POST /register`
- **Request Body**:
  ```json
  {
      "name": "User Name",
      "email": "user@example.com",
      "password": "userpassword",
        "role": "user" or 'admin'
  }
  ```
- **Response**: Success or error message.

### User Login
- **Endpoint**: `POST /login`
- **Request Body**:
  ```json
  {
      "email": "user@example.com",
      "password": "userpassword"
  }
  ```
- **Response**: Access token and user role.

### Add Train
- **Endpoint**: `POST /train`
- **Request Body**:
  ```json
  {
      "name": "Train Name",
      "source": "Source City",
      "destination": "Destination City",
      "total_seats": 100
  }
  ```
- **Authentication**: Admin only (JWT required).
- **Response**: Success or error message.

### Check Seat Availability
- **Endpoint**: `POST /availability`
- **Request Body**:
  ```json
  {
      "source": "Source City",
      "destination": "Destination City"
  }
  ```
- **Response**: List of trains with available seats.

### Book a Seat
- **Endpoint**: `POST /book`
- **Request Body**:
  ```json
  {
      "train_id": 1,
      "seats": 2
  }
  ```
- **Authentication**: JWT required.
- **Response**: Success message and booking ID.

### Get Booking Details
- **Endpoint**: `GET /booking/<int:booking_id>`
- **Authentication**: JWT required.
- **Response**: Details of the specified booking.

## Running the Application

To run the application, use the following command:

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000/`.
