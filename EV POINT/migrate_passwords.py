import sys
from werkzeug.security import generate_password_hash
from DBConnection import Db  # Your existing database connection

def migrate_passwords():
    db = Db()
    
    # Fetch all users with plaintext passwords (skip already hashed ones)
    users = db.select("""
        SELECT login_id, username, password 
        FROM login 
        WHERE password NOT LIKE 'pbkdf2:sha256:%'
    """)
    
    if not users:
        print("No plaintext passwords found. Migration not needed.")
        return
    
    print(f"Found {len(users)} users with plaintext passwords. Migrating...")
    
    for user in users:
        plain_password = user['password']
        hashed_password = generate_password_hash(plain_password)
        
        # Update the password in the database
        db.update("""
            UPDATE login 
            SET password = %s 
            WHERE login_id = %s
        """, (hashed_password, user['login_id']))
        
        print(f"✓ Updated {user['username']}")
    
    print("\nMigration complete!")

if __name__ == "__main__":
    print("=== Password Migration Script ===")
    migrate_passwords()