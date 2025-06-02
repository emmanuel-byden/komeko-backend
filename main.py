from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your Netlify frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL database URL
DATABASE_URL = "postgresql://username:password@localhost/dbname"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    event_date = Column(String, nullable=False)
    guests = Column(Integer, nullable=False)
    special_requests = Column(Text, nullable=True)

class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(Text, nullable=False)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Models for API endpoints
class BookingCreate(BaseModel):
    name: str
    email: str
    phone: str
    event_type: str
    event_date: str
    guests: int
    special_requests: str = None

class ContactCreate(BaseModel):
    name: str
    email: str
    message: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Booking endpoints
@app.post("/bookings/")
async def create_booking(booking: BookingCreate, db: SessionLocal = next(get_db())):
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return {"id": db_booking.id, "message": "Booking created successfully"}

@app.get("/bookings/{booking_id}")
async def read_booking(booking_id: int, db: SessionLocal = next(get_db())):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking:
        return {
            "id": booking.id,
            "name": booking.name,
            "email": booking.email,
            "phone": booking.phone,
            "event_type": booking.event_type,
            "event_date": booking.event_date,
            "guests": booking.guests,
            "special_requests": booking.special_requests
        }
    raise HTTPException(status_code=404, detail="Booking not found")

@app.get("/bookings/")
async def list_bookings(db: SessionLocal = next(get_db())):
    bookings = db.query(Booking).all()
    return [
        {
            "id": booking.id,
            "name": booking.name,
            "email": booking.email,
            "phone": booking.phone,
            "event_type": booking.event_type,
            "event_date": booking.event_date,
            "guests": booking.guests,
            "special_requests": booking.special_requests
        }
        for booking in bookings
    ]

# Contact endpoints
@app.post("/contacts/")
async def create_contact(contact: ContactCreate, db: SessionLocal = next(get_db())):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return {"id": db_contact.id, "message": "Contact message submitted successfully"}
