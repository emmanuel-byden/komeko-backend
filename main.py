from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

DATABASE_URL = "sqlite:///./test.db"  # Change to your database URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# Define the Booking model
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    event_type = Column(String)
    event_date = Column(String)  # Store as string in YYYY-MM-DD format
    guests = Column(Integer)
    special_requests = Column(String, nullable=True)

# Define the Contact model
class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(String)

Base.metadata.create_all(bind=engine)

# Pydantic model for Booking and Contact
class BookingCreate(BaseModel):
    name: str
    email: str
    phone: str
    event_type: str
    event_date: str
    guests: int
    special_requests: str = None

class BookingOut(BookingCreate):
    id: int

class ContactCreate(BaseModel):
    name: str
    email: str
    message: str

class ContactOut(ContactCreate):
    id: int

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Booking routes
@app.post("/bookings/", response_model=BookingOut)
async def create_booking(booking: BookingCreate, db: SessionLocal = next(get_db())):
    db_booking = Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@app.get("/bookings/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, db: SessionLocal = next(get_db())):
    booking = db.execute(select(Booking).where(Booking.id == booking_id)).scalars().first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

# Contact routes
@app.post("/contacts/", response_model=ContactOut)
async def create_contact(contact: ContactCreate, db: SessionLocal = next(get_db())):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact
