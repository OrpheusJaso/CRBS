"""Seed demo data so the prototype has users, resources and bookings to show.

Runs only when the tables are empty, so it is safe to call on every startup.
"""
from datetime import datetime, timedelta
from extensions import db
from models import (
    User, Resource, Booking, Notification, Equipment, EquipmentRequest,
)


def seed_demo_data():
    if User.query.first():
        return  # already seeded

    # One account per role (all share password 'password123').
    users = [
        ("u-student", "Nur Iman", "student@mmu.edu.my", "student"),
        ("u-staff", "Dr. Aisyah Rahman", "lecturer@mmu.edu.my", "staff"),
        ("u-manager", "Mr. Daniel", "manager@mmu.edu.my", "manager"),
        ("u-admin", "Admin User", "admin@mmu.edu.my", "admin"),
    ]
    for uid, name, email, role in users:
        u = User(userId=uid, name=name, email=email, role=role)
        u.set_password("password123")
        db.session.add(u)

    resources = [
        Resource(name="Meeting Room B-214", type="meeting room", capacity=24,
                 location="Faculty Building", status="available",
                 description="Whiteboard, video conference camera, HDMI display.",
                 isSpecialised=False),
        Resource(name="Computer Lab A-203", type="computer lab", capacity=40,
                 location="FCI Block", status="available",
                 description="40 PCs, projector, instructor station, wired network.",
                 isSpecialised=False),
        Resource(name="Projector P-04", type="projector", capacity=1,
                 location="AV Store", status="available",
                 description="High-lumen projector. Admin approval required.",
                 isSpecialised=True),
        Resource(name="Seminar Room C-101", type="meeting room", capacity=60,
                 location="Main Block", status="available",
                 description="Tiered seating, dual displays.", isSpecialised=False),
    ]
    db.session.add_all(resources)
    db.session.flush()  # assign resourceIds

    now = datetime.utcnow()
    staff = "u-staff"
    db.session.add_all([
        Booking(resourceId=resources[0].resourceId, userId=staff,
                purpose="Research group discussion",
                startTime=now + timedelta(hours=3), endTime=now + timedelta(hours=4),
                status="confirmed"),
        Booking(resourceId=resources[1].resourceId, userId=staff,
                purpose="Software Engineering lab",
                startTime=now + timedelta(days=2), endTime=now + timedelta(days=2, hours=2),
                status="confirmed"),
        Booking(resourceId=resources[2].resourceId, userId=staff,
                purpose="Guest lecture",
                startTime=now + timedelta(days=4), endTime=now + timedelta(days=4, hours=3),
                status="pending"),
    ])

    db.session.add_all([
        Notification(userId=staff, title="Check-in required",
                     message="Meeting Room B-214 starts soon. Confirm attendance.",
                     type="checkin"),
        Notification(userId=staff, title="Maintenance alert",
                     message="Projector P-04 is unavailable Friday 13:00-17:00.",
                     type="maintenance"),
    ])

    db.session.add_all([
        Equipment(name="High-lumen projector P-04", type="projector",
                  quantity=2, isSpecialised=True, condition="good"),
        Equipment(name="Wireless microphone set", type="audio",
                  quantity=5, isSpecialised=True, condition="good"),
        Equipment(name="Video conference kit", type="av",
                  quantity=3, isSpecialised=True, condition="good"),
    ])

    db.session.add(EquipmentRequest(
        userId=staff, equipmentName="High-lumen projector P-04",
        purpose="Guest lecture with external speaker",
        requestedDate=now + timedelta(days=5), attendees=80, status="pending",
    ))

    db.session.commit()
