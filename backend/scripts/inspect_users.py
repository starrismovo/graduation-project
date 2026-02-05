from database import SessionLocal
from models.user import User

print('Inspecting users via SQLAlchemy...')
db = SessionLocal()
try:
    users = db.query(User).all()
    if not users:
        print('No users found')
    for u in users:
        hashed = getattr(u, 'hashed_password', '') or ''
        print(f"{u.id}\t{u.username}\t{u.email}\t{(hashed[:10] + '...') if hashed else '<empty>'}\t{u.is_hr}")
except Exception as e:
    print('Error querying users:', e)
finally:
    db.close()
