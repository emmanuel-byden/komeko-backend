from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware (allow frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your Netlify frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite database file
DATABASE = 'bookings.db'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                guests INTEGER NOT NULL,
                special_requests TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            )
        ''')
        conn.commit()

# Call the database initialization function
init_db()

# Models for API endpoints
class Booking(BaseModel):
    name: str
    email: str
    phone: str
    event_type: str
    event_date: str
    guests: int
    special_requests: str = None

class Contact(BaseModel):
    name: str
    email: str
    message: str

# Booking endpoints
@app.post("/bookings/")
async def create_booking(booking: Booking):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (name, email, phone, event_type, event_date, guests, special_requests)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (booking.name, booking.email, booking.phone, booking.event_type, booking.event_date, booking.guests, booking.special_requests))
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Booking created successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/bookings/{booking_id}")
async def read_booking(booking_id: int):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
            booking = cursor.fetchone()
            if booking:
                return {
                    "id": booking[0],
                    "name": booking[1],
                    "email": booking[2],
                    "phone": booking[3],
                    "event_type": booking[4],
                    "event_date": booking[5],
                    "guests": booking[6],
                    "special_requests": booking[7]
                }
            raise HTTPException(status_code=404, detail="Booking not found")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/bookings/")
async def list_bookings():
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bookings')
            bookings = cursor.fetchall()
            return [
                {
                    "id": booking[0],
                    "name": booking[1],
                    "email": booking[2],
                    "phone": booking[3],
                    "event_type": booking[4],
                    "event_date": booking[5],
                    "guests": booking[6],
                    "special_requests": booking[7]
                }
                for booking in bookings
            ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# Contact endpoints
@app.post("/contacts/")
async def create_contact(contact: Contact):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contacts (name, email, message)
                VALUES (?, ?, ?)
            ''', (contact.name, contact.email, contact.message))
            conn.commit()
            return {"id": cursor.lastrowid, "message": "Contact message submitted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

