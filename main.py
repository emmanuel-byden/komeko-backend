from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLite database URL
DATABASE_URL = "sqlite:///./bookings.db"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    email: EmailStr
    phone: constr(min_length=10, max_length=15)  # Adjust length as needed
    event_type: str
    event_date: str
    guests: int
    special_requests: str = None

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    message: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Booking API!"}

# Favicon endpoint
@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse(None)  # Update the path as needed

# Booking endpoints
@app.post("/bookings/")
async def create_booking(booking: BookingCreate, db: SessionLocal = Depends(get_db)):
    try:
        db_booking = Booking(
            name=booking.name,
            email=booking.email,
            phone=booking.phone,
            event_type=booking.event_type,
            event_date=booking.event_date,
            guests=booking.guests,
            special_requests=booking.special_requests
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return {"id": db_booking.id, "message": "Booking created successfully"}
    except Exception as e:
        db.rollback()  # Rollback the transaction on error
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/bookings/{booking_id}")
async def read_booking(booking_id: int, db: SessionLocal = Depends(get_db)):
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
async def list_bookings(db: SessionLocal = Depends(get_db)):
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
async def create_contact(contact: ContactCreate, db: SessionLocal = Depends(get_db)):
    try:
        db_contact = Contact(**contact.dict())
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        return {"id": db_contact.id, "message": "Contact message submitted successfully"}
    except Exception as e:
        db.rollback()  # Rollback the transaction on error
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/contacts/")
async def list_contacts(db: SessionLocal = Depends(get_db)):
    contacts = db.query(Contact).all()
    return [
        {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "message": contact.message
        }
        for contact in contacts
    ]
