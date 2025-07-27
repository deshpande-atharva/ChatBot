from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from typing import Dict
import uuid

from .database import engine, Base, get_db
from .models import Session, Message, Vehicle
from .schemas import (
    SessionCreate, SessionResponse, MessageCreate, MessageResponse,
    VehicleCreate, ChatRequest, ChatResponse
)
from .chatbot import ChatBot
from .websocket_manager import ConnectionManager


# loading the environment variable when the server starts
load_dotenv()

# Create tables i they dont exist when the application starts.
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await manager.disconnect_all()

app = FastAPI(title="Bind IQ Onboarding Chatbot", lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
manager = ConnectionManager()

# ChatBot instance
chatbot = ChatBot()


# healthcheck to see if the backend is working fine
@app.get("/")
async def root():
    return {"message": "Bind IQ Onboarding Chatbot API"}

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    db = next(get_db())
    try:
        session = Session(
            id=str(uuid.uuid4()),
            status="active",
            current_step="zip_code",
            data={}
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Send initial greeting
        greeting = await chatbot.get_greeting()
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session.id,
            sender="bot",
            content=greeting
        )
        db.add(message)
        db.commit()
        
        return SessionResponse(
            id=session.id,
            status=session.status,
            current_step=session.current_step,
            created_at=session.created_at
        )
    finally:
        db.close()

@app.get("/api/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session details"""
    db = next(get_db())
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            id=session.id,
            status=session.status,
            current_step=session.current_step,
            created_at=session.created_at,
            data=session.data
        )
    finally:
        db.close()

@app.post("/api/debug-messages")
async def debug_messages(request: Request):
    """Debug endpoint to see raw request"""
    body = await request.body()
    headers = dict(request.headers)
    return {
        "headers": headers,
        "body": body.decode() if body else None,
        "content_type": request.headers.get("content-type")
    }

@app.post("/api/messages", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Process user message and return bot response"""
    db = next(get_db())
    try:
        # Get session
        session = db.query(Session).filter(Session.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Store the current step before processing
        current_step = session.current_step
        
        # Store user message
        user_message = Message(
            id=str(uuid.uuid4()),
            session_id=session.id,
            sender="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Broadcast user message via WebSocket
        await manager.broadcast(session.id, {
            "type": "message",
            "message": {
                "id": user_message.id,
                "sender": "user",
                "content": user_message.content,
                "created_at": user_message.created_at.isoformat()
            }
        })
        
        # Process message with chatbot
        response, next_step, extracted_data = await chatbot.process_message(
            request.message,
            session.current_step,
            session.data if session.data else {}
        )
        
        # Update session data if any data was extracted
        if extracted_data:
            print(f"DEBUG: Extracted data to save: {extracted_data}")
            
            # Initialize data if it's empty or None
            if not session.data:
                session.data = {}
                print("DEBUG: Initialized empty session.data")
            
            # Create a new dict to force SQLAlchemy to detect the change
            print(f"DEBUG: Session data BEFORE update: {session.data}")
            updated_data = dict(session.data)  # Make a copy
            updated_data.update(extracted_data)  # Update the copy
            session.data = updated_data  # Reassign to trigger SQLAlchemy
            print(f"DEBUG: Session data AFTER update: {session.data}")
            
        # Always update the current step if it changed
        if next_step != session.current_step:
            print(f"DEBUG: Updating step from {session.current_step} to {next_step}")
            session.current_step = next_step
            
        # Commit the changes
        db.commit()
        print(f"DEBUG: Changes committed to database")

        # Create vehicle record when we reach "add_another_vehicle" step
        if (next_step == "add_another_vehicle" and 
            current_step in ["commute_miles", "annual_mileage"] and
            "vehicle_info" in session.data):
            
            # Check if vehicle already exists for this session
            existing_vehicles = db.query(Vehicle).filter_by(session_id=session.id).count()
            
            if existing_vehicles == 0:  # Only create if no vehicles exist yet
                # Extract vehicle data
                vehicle_data = session.data.get("vehicle_info", {})
                
                # Create vehicle record
                new_vehicle = Vehicle(
                    id=str(uuid.uuid4()),
                    session_id=session.id,
                    vin=vehicle_data.get("vin"),
                    year=vehicle_data.get("year"),
                    make=vehicle_data.get("make"),
                    body_type=vehicle_data.get("body_type"),
                    vehicle_use=session.data.get("vehicle_use"),
                    blind_spot_warning=bool(session.data.get("blind_spot", False)),
                    commute_days_per_week=session.data.get("commute_days"),
                    commute_one_way_miles=session.data.get("commute_miles"),
                    annual_mileage=session.data.get("annual_mileage")
                )
                db.add(new_vehicle)
                db.commit()
                print(f"DEBUG: Created vehicle record {new_vehicle.id} for session {session.id}")

        # Refresh to get latest data
        db.refresh(session)
        print(f"DEBUG: Session data after refresh: {session.data}")
        
        # Store bot response
        bot_message = Message(
            id=str(uuid.uuid4()),
            session_id=session.id,
            sender="bot",
            content=response
        )
        db.add(bot_message)
        db.commit()
        
        # Broadcast bot message via WebSocket
        await manager.broadcast(session.id, {
            "type": "message",
            "message": {
                "id": bot_message.id,
                "sender": "bot",
                "content": bot_message.content,
                "created_at": bot_message.created_at.isoformat()
            }
        })
        
        # Check if session is complete
        if session.current_step == "complete":
            session.status = "completed"
            db.commit()
        
        return ChatResponse(
            message=response,
            current_step=session.current_step,
            session_status=session.status
        )
    finally:
        db.close()

@app.get("/api/messages/{session_id}")
async def get_messages(session_id: str):
    """Get all messages for a session"""
    db = next(get_db())
    try:
        messages = db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at).all()
        
        return [
            MessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                sender=msg.sender,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    finally:
        db.close()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(session_id, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for connection test
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

@app.post("/api/vehicles")
async def add_vehicle(vehicle: VehicleCreate):
    """Add a vehicle to a session"""
    db = next(get_db())
    try:
        # Verify session exists
        session = db.query(Session).filter(Session.id == vehicle.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create vehicle
        db_vehicle = Vehicle(
            id=str(uuid.uuid4()),
            **vehicle.dict()
        )
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        
        return {"id": db_vehicle.id, "message": "Vehicle added successfully"}
    finally:
        db.close()

@app.get("/api/vehicles/{session_id}")
async def get_vehicles(session_id: str):
    """Get all vehicles for a session"""
    db = next(get_db())
    try:
        vehicles = db.query(Vehicle).filter(
            Vehicle.session_id == session_id
        ).all()
        
        return vehicles
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)