"""
Toonify Pro: Premium Image Cartoonization Platform
Main Streamlit Application with Authentication, Payment Processing, and Image Processing

Features:
- User registration and authentication system
- Secure payment processing with Stripe integration
- Multiple cartoon filter styles with real-time parameter adjustment
- Download protection system (payment required)
- User account management and dashboard
- Professional UI with responsive design

Author: Vaidehi Jella
Updated: August 2026
Version: 2.0.0
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import base64
import time
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
import re
import secrets
import hashlib
import bcrypt
import stripe
import json

# Import custom modules
try:
    from utils.auth import AuthManager
    from utils.database import DatabaseManager
    from utils.payment import PaymentProcessor
    from utils.image_processing import ImageProcessor
    from utils.filters import FilterManager
    CUSTOM_MODULES_AVAILABLE = True
except ImportError:
    CUSTOM_MODULES_AVAILABLE = False

# Configuration
DATABASE_PATH = os.getenv("TOONIFY_DATABASE_PATH", "toonify_pro.db")

def get_secret(name: str, default: str = "") -> str:
    """Read a secret from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, default)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)

STRIPE_PUBLIC_KEY = get_secret("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = get_secret("STRIPE_SECRET_KEY")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Page configuration
st.set_page_config(
    page_title="Toonify Pro - Image Cartoonization",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://toonifypro.com/help',
        'Report a bug': 'https://toonifypro.com/support',
        'About': '''
        # Toonify Pro v2.0
        Professional image cartoonization platform with secure user accounts 
        and payment processing. Transform your photos into stunning artwork!
        '''
    }
)

# Enhanced CSS for professional appearance
st.markdown("""
<style>
/* Dark gradient background */
body, .main {
    background: linear-gradient(135deg, #141E30, #243B55);
    color: #ffffff;
    background-attachment: fixed;
    background-size: cover;
}

/* Glassmorphism effect for forms */
div.stForm {
    background: rgba(255, 255, 255, 0.08); /* transparent white layer */
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 15px;
    padding: 25px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

/* Style buttons */
div.stForm button, .stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 8px 18px;
    border: none;
    cursor: pointer;
    transition: 0.3s ease-in-out;
}

div.stForm button:hover, .stButton>button:hover {
    background: linear-gradient(135deg, #764ba2, #667eea);
    transform: scale(1.05);
}

/* Floating doodles container */
.doodles-container {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
}

.doodle {
    position: absolute;
    font-size: 3rem;
    opacity: 0.25;
    animation: float 6s ease-in-out infinite alternate;
}

.star { top: 10%; left: 15%; animation-delay: 0s; color: #fffd82; }
.paintbrush { top: 50%; left: 70%; animation-delay: 1.5s; color: #ffae42; }
.bubble { top: 75%; left: 30%; animation-delay: 3s; color: #81f7f3; }
.comic { top: 40%; left: 85%; animation-delay: 2s; color: #f28ab2; }
.sparkle { top: 20%; left: 55%; animation-delay: 4s; color: #fff48c; }

@keyframes float {
    0% { transform: translateY(0) translateX(0); }
    50% { transform: translateY(-20px) translateX(10px); }
    100% { transform: translateY(0) translateX(0); }
}
</style>

<div class="doodles-container">
  <span class="doodle star">✨</span>
  <span class="doodle paintbrush">🎨</span>
  <span class="doodle bubble">💥</span>
  <span class="doodle comic">🗯️</span>
  <span class="doodle sparkle">🌟</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Main styling */
    .main-header {
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        font-weight: 700;
    }
    
    .premium-badge {
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        color: #333;
        padding: 0.4rem 1.2rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 15px;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    /* Authentication forms */
    .auth-container {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border: 1px solid #e9ecef;
    }
    
    .auth-header {
        text-align: center;
        margin-bottom: 2rem;
        color: #333;
    }
    
    /* Payment section */
    .payment-section {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #28a745;
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.2);
    }
    
    .payment-section h3 {
        color: #155724;
        margin-bottom: 1rem;
        font-size: 2rem;
    }
    
    /* User dashboard */
    .user-info {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #28a745;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .user-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    
    .stat-item {
        text-align: center;
        flex: 1;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: bold;
        color: #28a745;
    }
    
    /* Pricing cards */
    .pricing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .pricing-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #007bff;
        position: relative;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .pricing-card.recommended {
        border-color: #28a745;
        background: linear-gradient(135deg, #f8fff9 0%, #e8f5e8 100%);
    }
    
    .recommended-badge {
        position: absolute;
        top: -10px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .price {
        font-size: 2.5rem;
        font-weight: bold;
        color: #333;
        margin: 1rem 0;
    }
    
    .price-features {
        list-style: none;
        padding: 0;
        margin: 1.5rem 0;
    }
    
    .price-features li {
        padding: 0.3rem 0;
        color: #555;
    }
    
    .price-features li:before {
        content: "✓ ";
        color: #28a745;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    /* Download section */
    .download-ready {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #28a745;
    }
    
    .download-locked {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #856404;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .payment-button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 1rem 2.5rem !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        margin: 0.5rem !important;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e9ecef;
        padding: 0.8rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Image containers */
    .image-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .image-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
        text-align: center;
    }
    
    /* Processing indicators */
    .processing-container {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #2196f3;
    }
    
    /* Feature showcase */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e9ecef;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #333;
    }
    
    /* Metrics and stats */
    .metrics-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .metric-item {
        text-align: center;
        margin: 1rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .pricing-grid {
            grid-template-columns: 1fr;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# Fallback implementations for when custom modules aren't available
class SimpleAuthManager:
    """Simplified authentication manager with essential security features."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize user database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                downloads_count INTEGER DEFAULT 0,
                total_spent DECIMAL(10,2) DEFAULT 0.00
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                plan_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'completed',
                stripe_payment_intent_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Album table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filter_type TEXT NOT NULL,
                processing_time_seconds REAL NOT NULL,
                image_width INTEGER,
                image_height INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except:
            # Fallback to SHA256 if bcrypt unavailable
            return hashlib.sha256((password + "salt").encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            # Fallback verification
            return hashlib.sha256((password + "salt").encode()).hexdigest() == hashed
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        return True, "Password is strong"
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str, last_name: str) -> Tuple[bool, str]:
        """Create new user account with validation."""
        # Input validation
        if not all([username, email, password, first_name, last_name]):
            return False, "All fields are required"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        password_valid, password_message = self.validate_password_strength(password)
        if not password_valid:
            return False, password_message
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
            if cursor.fetchone():
                conn.close()
                return False, "Email or username already exists"
            
            # Create user
            password_hash = self.hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
            """, (username, email, password_hash, first_name, last_name))
            
            conn.commit()
            conn.close()
            return True, "Account created successfully"
            
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error creating account: {str(e)}"
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user login."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, password_hash, first_name, last_name, 
                       downloads_count, total_spent FROM users 
                WHERE email = ? AND is_active = TRUE
            """, (email,))
            
            user_data = cursor.fetchone()
            if not user_data or not self.verify_password(password, user_data[2]):
                conn.close()
                return None
            
            # Update last login
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                         (datetime.now().isoformat(), user_data[0]))
            conn.commit()
            conn.close()
            
            return {
                'id': user_data[0],
                'username': user_data[1],
                'first_name': user_data[3],
                'last_name': user_data[4],
                'downloads_count': user_data[5],
                'total_spent': float(user_data[6])
            }
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
        
    def update_user_profile(self, user_id: int, first_name: str, last_name: str, username: str, email: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users
                SET first_name = ?, last_name = ?, username = ?, email = ?
                WHERE id = ?
            """, (first_name, last_name, username, email, user_id))
            conn.commit()
            return True, "Profile updated successfully"
        except Exception as e:
            return False, f"Error updating profile: {e}"
        finally:
            conn.close()

    
    def get_user_info(self, user_id: int) -> Dict:
        """Get user information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, email, first_name, last_name, created_at, 
                       last_login, downloads_count, total_spent
                FROM users WHERE id = ?
            """, (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    'username': user_data[0],
                    'email': user_data[1],
                    'first_name': user_data[2],
                    'last_name': user_data[3],
                    'created_at': user_data[4],
                    'last_login': user_data[5],
                    'downloads_count': user_data[6],
                    'total_spent': float(user_data[7])
                }
            return {}
        except Exception:
            return {}
    
    
    def save_album_image(self, user_id: int, image_array) -> str:
        filename = f"user_albums/{user_id}_{int(time.time())}.png"
        os.makedirs("user_albums", exist_ok=True)
        Image.fromarray(image_array).save(filename)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_albums (user_id,image_path) VALUES (?,?)", (user_id, filename))
        conn.commit()
        conn.close()
        return filename

    def get_user_album(self, user_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT image_path, created_at FROM user_albums WHERE user_id=? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_albums")
        total_images = cursor.fetchone()[0]
        cursor.execute("SELECT DATE(created_at), COUNT(*) FROM user_albums GROUP BY DATE(created_at)")
        data = cursor.fetchall()
        conn.close()
        return total_users, total_images, data

    def record_transaction(self, user_id: int, amount: float, plan_type: str,
                           stripe_payment_intent_id: Optional[str] = None) -> bool:
        """Record a successful Stripe test transaction and update user stats."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions
                    (user_id, amount, plan_type, status, stripe_payment_intent_id)
                VALUES (?, ?, ?, 'completed', ?)
            """, (user_id, amount, plan_type, stripe_payment_intent_id))
            cursor.execute("""
                UPDATE users
                SET downloads_count = downloads_count + 1, total_spent = total_spent + ?
                WHERE id = ?
            """, (amount, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Transaction error: {e}")
            return False

    def record_processing_metric(self, user_id: int, filter_type: str,
                                 processing_time_seconds: float, image_shape) -> bool:
        """Persist real filter execution timing for later performance reporting."""
        try:
            height, width = image_shape[:2]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_metrics
                    (user_id, filter_type, processing_time_seconds, image_width, image_height)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, filter_type, processing_time_seconds, width, height))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Processing metric error: {e}")
            return False
        
    def update_user_profile(self, user_id, first_name=None, last_name=None, username=None, email=None):
        """Update user profile info in SQLite DB."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build dynamic update query
            fields, values = [], []
            if first_name:
                fields.append("first_name = ?")
                values.append(first_name)
            if last_name:
                fields.append("last_name = ?")
                values.append(last_name)
            if username:
                fields.append("username = ?")
                values.append(username)
            if email:
                fields.append("email = ?")
                values.append(email)

            if not fields:
                conn.close()
                return False, "No changes provided"

            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            values.append(user_id)
            cursor.execute(query, tuple(values))
            conn.commit()
            conn.close()

            return True, "Profile updated successfully"

        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error updating profile: {str(e)}"
                

    def change_password(self, user_id: int, current_password: str, new_password: str):
        """Change user password securely."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current hash
            cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False, "User not found"

            stored_hash = row[0]

            # Verify current password
            if not self.verify_password(current_password, stored_hash):
                conn.close()
                return False, "Current password is incorrect"

            # Validate new password strength
            valid, msg = self.validate_password_strength(new_password)
            if not valid:
                conn.close()
                return False, msg

            # Update new password
            new_hash = self.hash_password(new_password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
            conn.commit()
            conn.close()

            return True, "Password updated successfully"

        except Exception as e:
            return False, f"Error changing password: {str(e)}"



class SimpleFilterManager:
    """Enhanced filter manager with professional cartoon effects."""
    
    def __init__(self):
        self.processor = SimpleImageProcessor()
    
    def get_available_filters(self) -> Dict[str, Dict[str, Any]]:
        """Get all available filters with descriptions."""
        return {
            'classic': {
                'name': 'Classic Cartoon',
                'description': 'Traditional cartoon effect with smooth colors and bold edges',
                'parameters': ['edge_thickness', 'color_smoothing', 'blur_strength'],
                'icon': '🎭'
            },
            'sketch': {
                'name': 'Sketch Effect',
                'description': 'Black and white pencil sketch style',
                'parameters': ['edge_thickness', 'blur_strength'],
                'icon': '✏️'
            },
            'color_pencil': {
                'name': 'Color Pencil',
                'description': 'Colored pencil drawing effect with artistic texture',
                'parameters': ['edge_thickness', 'color_smoothing', 'blur_strength'],
                'icon': '🖍️'
            },
            'oil_painting': {
                'name': 'Oil Painting',
                'description': 'Rich oil painting style with textured brushstrokes',
                'parameters': ['color_smoothing', 'blur_strength'],
                'icon': '🎨'
            },
            'watercolor': {
                'name': 'Watercolor',
                'description': 'Soft watercolor painting with flowing colors',
                'parameters': ['color_smoothing', 'blur_strength'],
                'icon': '🌊'
            },
            'anime': {
                'name': 'Anime Style',
                'description': 'Anime/manga style with flat colors and bold outlines',
                'parameters': ['edge_thickness', 'color_smoothing'],
                'icon': '🌟'
            }
        }
    
    
        
    def apply_filter(self, image: np.ndarray, filter_type: str, 
                 parameters: Optional[Dict[str, Any]] = None) -> np.ndarray:
      """Apply selected filter with parameters."""
      if parameters is None:
        parameters = {}

    # 🔹 Ensure correct format here
      if image.shape[-1] == 4:  # RGBA → BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
      elif len(image.shape) == 2 or image.shape[-1] == 1:  # Gray → BGR
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
      if image.dtype != np.uint8:
        image = cv2.convertScaleAbs(image)

      processed_image = self.processor.preprocess_image(image)

      filter_methods = {
        'classic': self._apply_classic_cartoon,
        'sketch': self._apply_sketch_effect,
        'color_pencil': self._apply_color_pencil,
        'oil_painting': self._apply_oil_painting,
        'watercolor': self._apply_watercolor,
        'anime': self._apply_anime_style
      }

      if filter_type in filter_methods:
        result = filter_methods[filter_type](processed_image, parameters)
      else:
        result = processed_image

      return self.processor.postprocess_image(result, output_format="RGB")
    
    def _apply_classic_cartoon(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply classic cartoon effect."""
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)
        blur_strength = params.get('blur_strength', 3)
        
        # Apply bilateral filter for smooth colors
        smooth = cv2.bilateralFilter(image, color_smoothing * 2 + 1, 
                                   color_smoothing * 20, color_smoothing * 20)
        
        # Create edge mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                     cv2.THRESH_BINARY, edge_thickness * 2 + 1, blur_strength)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine smooth image with edges
        cartoon = cv2.bitwise_and(smooth, edges)
        return cartoon
    
    def _apply_sketch_effect(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply pencil sketch effect."""
        blur_strength = params.get('blur_strength', 3)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        
        # Apply Gaussian blur
        kernel_size = blur_strength * 4 + 1
        blurred = cv2.GaussianBlur(inverted, (kernel_size, kernel_size), 0)
        
        # Create sketch using dodge blending
        sketch = cv2.divide(gray, 255 - blurred, scale=256.0)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    
    def _apply_color_pencil(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply colored pencil effect."""
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)
        blur_strength = params.get('blur_strength', 3)
        
        # Light bilateral filtering
        smooth = cv2.bilateralFilter(image, color_smoothing, 
                                   color_smoothing * 10, color_smoothing * 10)
        
        # Create soft edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                     cv2.THRESH_BINARY, edge_thickness * 2 + 1, blur_strength)
        
        # Convert edges and blend
        edges_3ch = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
        result = (smooth.astype(np.float32) * edges_3ch).astype(np.uint8)
        
        # Enhance contrast
        result = cv2.convertScaleAbs(result, alpha=1.2, beta=10)
        return result
    
    def _apply_oil_painting(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply oil painting effect."""
        color_smoothing = params.get('color_smoothing', 7)
        
        # Multiple bilateral filters for oil painting texture
        smooth1 = cv2.bilateralFilter(image, 15, 80, 80)
        smooth2 = cv2.bilateralFilter(smooth1, 15, 80, 80)
        
        # Color quantization
        data = smooth2.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 6, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized_data = centers[labels.flatten()]
        return quantized_data.reshape(smooth2.shape)
    
    def _apply_watercolor(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply watercolor effect."""
        # Multiple bilateral filters
        smooth1 = cv2.bilateralFilter(image, 15, 80, 80)
        smooth2 = cv2.bilateralFilter(smooth1, 15, 80, 80)
        
        # Color quantization for watercolor palette
        data = smooth2.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 6, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized_data = centers[labels.flatten()]
        quantized = quantized_data.reshape(smooth2.shape)
        
        # Soft blur for watercolor effect
        watercolor = cv2.GaussianBlur(quantized, (3, 3), 0)
        return watercolor
    
    def _apply_anime_style(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply anime/manga style effect."""
        edge_thickness = params.get('edge_thickness', 5)
        color_smoothing = params.get('color_smoothing', 7)
        
        # Strong bilateral filtering for flat colors
        smooth = cv2.bilateralFilter(image, color_smoothing * 3, 
                                   color_smoothing * 25, color_smoothing * 25)
        
        # Aggressive color quantization
        data = smooth.reshape((-1, 3))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(data, 5, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        quantized_data = centers[labels.flatten()]
        quantized = quantized_data.reshape(smooth.shape)
        
        # Enhance saturation
        hsv = cv2.cvtColor(quantized, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)
        quantized = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Strong edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                     cv2.THRESH_BINARY, edge_thickness * 2 + 1, 5)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Combine
        anime = cv2.bitwise_and(quantized, edges)
        return anime

class SimpleImageProcessor:
    """Image processor with OpenCV utilities."""
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for processing."""
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return np.clip(image, 0, 255).astype(np.uint8)
    
    def postprocess_image(self, image: np.ndarray, output_format: str = "RGB") -> np.ndarray:
        """Postprocess image for display."""
        if output_format == "RGB" and len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return np.clip(image, 0, 255).astype(np.uint8)

# Session state initialization
def init_session_state():
    """Initialize session state variables."""
    session_vars = {
        'user_authenticated': False,
        'user_id': None,
        'username': None,
        'user_data': None,
        'processed_image': None,
        'original_image': None,
        'current_filter': None,
        'payment_completed': False,
        'payment_plan': None,
        'payment_amount': 0.0,
        'show_signup': False,
        'processing_time': 0.0,
        'uploaded_file_id': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# Authentication UI components
def show_login_form():
    """Display professional login form."""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h2>🔐 Welcome Back</h2>
            <p>Sign in to your Toonify Pro account</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col_login, col_signup = st.columns(2)
            
            with col_login:
                login_submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            with col_signup:
                if st.form_submit_button("📝 Create Account", use_container_width=True):
                    st.session_state.show_signup = True
                    st.rerun()
        
        if login_submitted and email and password:
            auth_manager = SimpleAuthManager()
            user_data = auth_manager.authenticate_user(email, password)
            
            if user_data:
                st.session_state.user_authenticated = True
                st.session_state.user_id = user_data['id']
                st.session_state.username = user_data['username']
                st.session_state.user_data = user_data
                st.success(f"✅ Welcome back, {user_data['first_name']}!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Invalid email or password. Please try again.")

def show_signup_form():
    """Display professional signup form."""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h2>📝 Create Your Account</h2>
            <p>Join Toonify Pro and start creating amazing artwork</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("signup_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            col_first, col_last = st.columns(2)
            with col_first:
                first_name = st.text_input("👤 First Name", placeholder="First name")
            with col_last:
                last_name = st.text_input("👤 Last Name", placeholder="Last name")
            
            username = st.text_input("🏷️ Username", placeholder="Choose a username")
            email = st.text_input("📧 Email Address", placeholder="Enter your email")
            
            password = st.text_input("🔒 Password", type="password", placeholder="Create password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")

            
            terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            
            col_create, col_back = st.columns(2)
            
            with col_create:
                signup_submitted = st.form_submit_button("🎯 Create Account", use_container_width=True)
            
            with col_back:
                if st.form_submit_button("🔙 Back to Login", use_container_width=True):
                    st.session_state.show_signup = False
                    st.rerun()
        
        if signup_submitted:
            # Comprehensive validation
            errors = []
            
            if not all([first_name, last_name, username, email, password, confirm_password]):
                errors.append("All fields are required")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if not terms_accepted:
                errors.append("You must accept the terms and conditions")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                auth_manager = SimpleAuthManager()
                success, message = auth_manager.create_user(
                    username, email, password, first_name, last_name
                )
                
                if success:
                    st.success("✅ Account created successfully! Please sign in.")
                    st.session_state.show_signup = False
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


def show_profile_page():
    if not st.session_state.get("user_authenticated"):
        st.warning("⚠️ Please log in first.")
        return
    user = st.session_state["user_data"]
    st.markdown(f"## 👤 Account Settings for {user.get('username', '')}")
    # Update profile info
    with st.expander("✏️ Update Profile"):
        with st.form("update_profile_form"):
            new_first = st.text_input("First Name", value=user.get('first_name', ''))
            new_last = st.text_input("Last Name", value=user.get('last_name', ''))
            new_username = st.text_input("Username", value=user.get('username', ''))
            new_email = st.text_input("Email", value=user.get('email', ''))
            save = st.form_submit_button("💾 Save Changes")
            if save:
                auth_manager = SimpleAuthManager()
                success, msg = auth_manager.update_user_profile(
                    user.get('id'),
                    first_name=new_first,
                    last_name=new_last,
                    username=new_username,
                    email=new_email
               )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    # Change password
    with st.expander("🔑 Change Password"):
        with st.form("change_password_form"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            change = st.form_submit_button("🔄 Update Password")
            if change:
                if new_pw != confirm_pw:
                    st.error("New passwords do not match")
                else:
                    auth_manager = SimpleAuthManager()
                    success, msg = auth_manager.change_password(user['id'], current_pw, new_pw)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
    if st.button("🚪 Logout"):
        st.session_state.user_authenticated = False
        st.session_state.user_data = None
        st.success("Logged out successfully")
        st.rerun()


        

def show_user_dashboard():
    """Display enhanced user dashboard."""
    if st.session_state.user_data:
        user = st.session_state.user_data
        
        st.markdown(f"""
        <div class="user-info">
            <h4>👤 Welcome, {user.get('first_name', 'User')} {user.get('last_name', '')}!</h4>
            <div class="user-stats">
                <div class="stat-item">
                    <div class="stat-number">{user.get('downloads_count', 0)}</div>
                    <div class="stat-label">Downloads</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${user.get('total_spent', 0):.2f}</div>
                    <div class="stat-label">Total Spent</div>
                </div>
            </div>
            <p style="margin-top: 1rem;"><strong>Username:</strong> {user.get('username', 'N/A')}</p>
            <p><strong>Email:</strong> {user.get('email', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔓 Sign Out", use_container_width=True):
            # Clear all session data
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Payment processing components
def show_payment_section():
    """Display professional payment interface."""
    st.markdown("""
    <div class="payment-section">
        <h3>💎 Premium Download</h3>
        <p>Your cartoon image is ready! Choose a plan to download your high-quality artwork.</p>
    </div>
    """, unsafe_allow_html=True)
    
    
    # Payment buttons
        # Payment buttons
        # Payment buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "💳 Select Basic - $2.99",
            key="payment_plan_basic",
            width="stretch"
        ):
            process_payment(2.99, "basic")

    with col2:
        if st.button(
            "💳 Select Premium - $4.99",
            key="payment_plan_premium",
            width="stretch"
        ):
            process_payment(4.99, "premium")

    with col3:
        if st.button(
            "💳 Select Pro - $7.99",
            key="payment_plan_pro",
            width="stretch"
        ):
            process_payment(7.99, "pro")
    

def process_payment(amount: float, plan_type: str):
    """Create and confirm a real Stripe test-mode PaymentIntent."""
    if not STRIPE_SECRET_KEY:
        st.error("Stripe test mode is not configured. Add STRIPE_SECRET_KEY to .streamlit/secrets.toml locally or to Streamlit Cloud Secrets.")
        return

    if not STRIPE_SECRET_KEY.startswith("sk_test_"):
        st.error("For this portfolio project, only Stripe test-mode secret keys are accepted.")
        return

    try:
        with st.spinner("Processing secure Stripe test payment..."):
            payment_intent = stripe.PaymentIntent.create(
                amount=int(round(amount * 100)),
                currency="usd",
                payment_method="pm_card_visa",
                confirm=True,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
                metadata={
                    "toonify_plan": plan_type,
                    "toonify_user_id": str(st.session_state.user_id),
                },
                description=f"Toonify Pro {plan_type.title()} test purchase",
            )

        if payment_intent.status != "succeeded":
            st.error(f"Stripe test payment was not completed (status: {payment_intent.status}).")
            return

        auth_manager = SimpleAuthManager()
        if not auth_manager.record_transaction(
            st.session_state.user_id, amount, plan_type, payment_intent.id
        ):
            st.error("Stripe succeeded, but the local transaction could not be recorded.")
            return

        st.session_state.payment_completed = True
        st.session_state.payment_amount = amount
        st.session_state.payment_plan = plan_type
        st.session_state.user_data['total_spent'] += amount
        st.session_state.user_data['downloads_count'] += 1

        st.success(f"✅ Stripe test payment of ${amount:.2f} succeeded. PaymentIntent: {payment_intent.id}")
        st.balloons()
        st.rerun()

    except stripe.StripeError as e:
        message = getattr(e, "user_message", None) or str(e)
        st.error(f"❌ Stripe test payment failed: {message}")
    except Exception as e:
        st.error(f"❌ Payment processing error: {str(e)}")

def show_download_section():
    """Display enhanced download interface."""
    if st.session_state.payment_completed:
        plan_type = st.session_state.get('payment_plan', 'basic')
        
        st.markdown(f"""
        <div class="download-ready">
            <h3>🎉 Download Ready!</h3>
            <p>Payment confirmed! Your {plan_type.title()} plan download is ready.</p>
            <p><strong>Amount Paid:</strong> ${st.session_state.payment_amount:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate downloads based on plan
        if plan_type == "basic":
            filename = f"toonify_basic_{st.session_state.current_filter}_{int(time.time())}.png"
            download_data = create_download_data(st.session_state.processed_image, "PNG", quality=85)
            
            st.download_button(
                label="📥 Download PNG Image (Standard Quality)",
                data=download_data,
                file_name=filename,
                mime="image/png",
                use_container_width=True
            )
            
        elif plan_type == "premium":
            col1, col2 = st.columns(2)
            
            with col1:
                filename_png = f"toonify_premium_{st.session_state.current_filter}_{int(time.time())}.png"
                download_data_png = create_download_data(st.session_state.processed_image, "PNG", quality=95)
                
                st.download_button(
                    label="📥 Download PNG (High Quality)",
                    data=download_data_png,
                    file_name=filename_png,
                    mime="image/png",
                    use_container_width=True
                )
            
            with col2:
                filename_jpg = f"toonify_premium_{st.session_state.current_filter}_{int(time.time())}.jpg"
                download_data_jpg = create_download_data(st.session_state.processed_image, "JPEG", quality=90)
                
                st.download_button(
                    label="📥 Download JPEG (Optimized)",
                    data=download_data_jpg,
                    file_name=filename_jpg,
                    mime="image/jpeg",
                    use_container_width=True
                )
                
        else:  # pro plan
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filename_png = f"toonify_pro_{st.session_state.current_filter}_{int(time.time())}.png"
                download_data_png = create_download_data(st.session_state.processed_image, "PNG", quality=100)
                
                st.download_button(
                    label="📥 Ultra HD PNG",
                    data=download_data_png,
                    file_name=filename_png,
                    mime="image/png",
                    use_container_width=True
                )
            
            with col2:
                filename_jpg = f"toonify_pro_{st.session_state.current_filter}_{int(time.time())}.jpg"
                download_data_jpg = create_download_data(st.session_state.processed_image, "JPEG", quality=95)
                
                st.download_button(
                    label="📥 High Quality JPEG",
                    data=download_data_jpg,
                    file_name=filename_jpg,
                    mime="image/jpeg",
                    use_container_width=True
                )
            
            with col3:
                filename_print = f"toonify_print_{st.session_state.current_filter}_{int(time.time())}.png"
                
                st.download_button(
                    label="🖨️ Print Ready (300 DPI)",
                    data=download_data_png,
                    file_name=filename_print,
                    mime="image/png",
                    use_container_width=True
                )
        
        # Show success metrics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Processing Time", f"{st.session_state.processing_time:.2f}s")
        with col2:
            st.metric("Plan Selected", plan_type.title())
        with col3:
            st.metric("Status", "✅ Complete")
    
    else:
        st.markdown("""
        <div class="download-locked">
            <h3>🔒 Download Locked</h3>
            <p>Complete payment to unlock your high-quality cartoon image download.</p>
        </div>
        """, unsafe_allow_html=True)

# Utility functions
def create_download_data(image: np.ndarray, format_type: str, quality: int = 95) -> bytes:
    """Create optimized download data."""
    pil_image = Image.fromarray(image.astype('uint8'))
    img_buffer = io.BytesIO()
    
    if format_type == "PNG":
        pil_image.save(img_buffer, format='PNG', optimize=True)
    elif format_type == "JPEG":
        pil_image.save(img_buffer, format='JPEG', quality=quality, optimize=True)
    
    return img_buffer.getvalue()

def validate_image(uploaded_file) -> Tuple[bool, str]:
    """Comprehensive image validation."""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # File size validation (10MB limit)
    if uploaded_file.size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit. Please use a smaller image."
    
    # File type validation
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if uploaded_file.type not in allowed_types:
        return False, "Unsupported file format. Please use JPG, PNG, or WebP images."
    
    # Additional validation
    try:
        image = Image.open(uploaded_file)
        width, height = image.size
        
        if width < 100 or height < 100:
            return False, "Image too small. Minimum size is 100x100 pixels."
        
        if width > 6000 or height > 6000:
            return False, "Image too large. Maximum size is 6000x6000 pixels."

        return True, "Valid image file"
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def show_feature_showcase():
    """Display feature showcase for non-authenticated users."""
    st.markdown("---")
    st.markdown("## ✨ Toonify Pro Features")
    st.markdown("""
    - **Professional Filters**: 6 advanced cartoon filters including Classic, Sketch, Oil Painting, Watercolor, Anime Style, and Color Pencil effects.
    - **Secure Platform**: Advanced user authentication, secure payment processing, download history tracking, and complete privacy protection.
    - **Premium Quality**: High-resolution output up to 4K, multiple format options, commercial licensing, and priority processing.
    - **Advanced Controls**: Real-time parameter adjustment, custom settings, preview modes, and professional-grade image processing.
    - **Easy to Use**: Intuitive interface, drag-and-drop uploads, instant previews, and seamless user experience across all devices.
    - **Fast Processing**: Optimized algorithms, cloud processing, instant results, and efficient handling of large images.
    """)

# Main application
def main():
    init_session_state()
    # ------------------ ADMIN LOGIN CHECK ------------------ #
    page = st.sidebar.radio("Navigation", ["Home", "Album",  "Profile", "Admin"])

    if page == "Admin":
        if not st.session_state.get("is_admin", False):
            if st.session_state.user_authenticated and st.session_state.user_data.get("email") == "jellavaidehi49@gmail.com":
                st.sidebar.markdown("### 🔑 Admin Access")
                admin_pw = st.sidebar.text_input("Enter Admin Password", type="password")
                if admin_pw == "Virat@18":
                    st.session_state.is_admin = True
                    st.success("✅ Admin access granted")
                    st.rerun()

    if st.session_state.get("is_admin", False):
        st.title("📊 Admin Dashboard")
        users, images, data = SimpleAuthManager().get_stats()
        st.metric("Total Users", users)
        st.metric("Images Converted", images)

        if data:
            import matplotlib.pyplot as plt
            dates = [d[0] for d in data]
            counts = [d[1] for d in data]
            fig, ax = plt.subplots()
            ax.plot(dates, counts, marker="o")
            ax.set_title("Images Converted Over Time")
            st.pyplot(fig)
        return

    # ------------------ ALBUM PAGE ------------------ #
    if page == "Album":
        st.title("📸 Your Album")
        rows = SimpleAuthManager().get_user_album(st.session_state.user_id)
        if rows:
            for path, created in rows:
                st.image(path, caption=f"Created on {created}")
        else:
            st.info("No images yet.")



    """Main application with enhanced features."""

    # Initialize session state
    init_session_state()

    # Application header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Toonify Pro <span class="premium-badge">PREMIUM</span></h1>
        <p>Professional image cartoonization with secure accounts and premium downloads</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- AUTHENTICATION ---------------- #
    if not st.session_state.user_authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.session_state.show_signup:
                show_signup_form()
            else:
                show_login_form()

    else:
        # ---------------- SIGNED-IN USER AREA ---------------- #
        show_profile_page()

        with st.sidebar:
            show_user_dashboard()
            st.markdown("---")

            # Image upload
            st.markdown("### 📁 Upload Your Image")
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['jpg', 'jpeg', 'png', 'webp'],
                help="Upload JPG, PNG, or WebP images (max 10MB)"
            )

            if uploaded_file is not None:
                is_valid, validation_message = validate_image(uploaded_file)

                if not is_valid:
                    st.error(f"❌ {validation_message}")
                    return

            try:
                current_file_id = (
                    uploaded_file.name,
                    uploaded_file.size
                )

                # Only load/reset when a NEW image is uploaded
                if st.session_state.uploaded_file_id != current_file_id:
                    image = Image.open(uploaded_file)

                    st.session_state.original_image = np.array(image)
                    st.session_state.processed_image = None
                    st.session_state.payment_completed = False
                    st.session_state.payment_plan = None
                    st.session_state.payment_amount = 0.0
                    st.session_state.uploaded_file_id = current_file_id

                    st.success("✅ Image loaded successfully!")
                    st.info(
                        f"📏 Size: {image.size[0]}×{image.size[1]} pixels"
                    )

            except Exception as e:
                st.error(f"❌ Error loading image: {str(e)}")
                return

            # Filter controls (only if an image is uploaded)
            if st.session_state.original_image is not None:
                st.markdown("---")
                st.markdown("### 🎨 Choose Your Style")

                filter_manager = SimpleFilterManager()
                available_filters = filter_manager.get_available_filters()

                # Filter selection
                filter_options = {
                    f"{info['icon']} {info['name']}": key
                    for key, info in available_filters.items()
                }

                selected_filter_display = st.selectbox(
                    "Select cartoon style:",
                    options=list(filter_options.keys()),
                    index=0,
                    help="Choose the artistic style for your image"
                )

                st.session_state.current_filter = filter_options[selected_filter_display]
                current_filter_info = available_filters[st.session_state.current_filter]

                st.info(f"ℹ️ {current_filter_info['description']}")

                # Parameter controls
                st.markdown("---")
                st.markdown("### ⚙️ Fine-tune Settings")

                parameters = {}
                if 'edge_thickness' in current_filter_info['parameters']:
                    parameters['edge_thickness'] = st.slider("Edge Thickness", 1, 15, 5)
                if 'color_smoothing' in current_filter_info['parameters']:
                    parameters['color_smoothing'] = st.slider("Color Smoothing", 1, 15, 7)
                if 'blur_strength' in current_filter_info['parameters']:
                    parameters['blur_strength'] = st.slider("Blur Strength", 1, 10, 3)

                # Processing buttons
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("🎨 Apply Filter", type="primary", use_container_width=True):
                        try:
                            start_time = time.perf_counter()
                            with st.spinner(f"Applying {current_filter_info['name']}..."):
                                processed_img = filter_manager.apply_filter(
                                    st.session_state.original_image,
                                    st.session_state.current_filter,
                                    parameters
                                )   
                                st.session_state.processed_image = processed_img
                                st.session_state.processing_time = time.perf_counter() - start_time
                                st.session_state.payment_completed = False

            # 🔹 Save processed image to album immediately
                                try:
                                    auth_manager = SimpleAuthManager()
                                    auth_manager.save_album_image(
                                    st.session_state.user_id,
                                    st.session_state.processed_image
                                    )
                                    auth_manager.record_processing_metric(
                                        st.session_state.user_id,
                                        st.session_state.current_filter,
                                        st.session_state.processing_time,
                                        st.session_state.original_image.shape
                                    )
                                except Exception as e:
                                    st.warning(f"⚠️ Filter applied but image not saved to album: {e}")

                            st.success(f"✅ Filter applied! ({st.session_state.processing_time:.2f}s)")
                        except Exception as e:
                            st.error(f"❌ Processing error: {str(e)}")


                with col2:
                    if st.button("🔄 Reset Settings", use_container_width=True):
                        st.rerun()

        # ---------------- MAIN CONTENT AREA ---------------- #
        if st.session_state.original_image is not None:
            st.markdown("## 📸 Image Comparison")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="image-title">Original Image</div>', unsafe_allow_html=True)
                st.image(st.session_state.original_image, use_container_width=True, caption="Your uploaded image")

            with col2:
                st.markdown('<div class="image-title">Cartoon Effect</div>', unsafe_allow_html=True)
                if st.session_state.processed_image is not None:
                    st.image(
                        st.session_state.processed_image,
                        use_container_width=True,
                        caption=f"Processed with {available_filters[st.session_state.current_filter]['name']}"
                    )
                else:
                    st.info("👆 Select a filter and click 'Apply Filter' to see the magic!")

            # Payment/download
            if st.session_state.processed_image is not None:
                st.markdown("---")
                if not st.session_state.payment_completed:
                    show_payment_section()
                else:
                    show_download_section()

        else:
            # ✅ Welcome screen for authenticated users only
            st.markdown("""
            ## 🎉 Welcome to Toonify Pro!
            You're signed in and ready to create amazing cartoon artwork!

            ### 🚀 Getting Started:
            1. **📁 Upload an image** using the sidebar file uploader
            2. **🎨 Choose a filter** from our collection of 6 professional styles
            3. **⚙️ Adjust parameters** with real-time sliders for perfect results
            4. **💳 Complete payment** to unlock high-quality downloads
            5. **📥 Download** your professional cartoon artwork

            ### 🌟 Your Premium Benefits:
            - ✅ Access to all 6 professional cartoon filters
            - ✅ High-resolution output options (up to 4K)
            - ✅ Multiple download formats (PNG, JPEG)
            - ✅ Secure payment processing with Stripe
            - ✅ Download history and account management
            - ✅ Commercial licensing options
            - ✅ Priority customer support

            **Ready to create?** Upload your first image using the sidebar! 👈
            """)

            


if __name__ == "__main__":
    main()