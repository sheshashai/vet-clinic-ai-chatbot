import os
import json
from datetime import datetime, timedelta, time, date
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask.json.provider import DefaultJSONProvider
from sqlalchemy import text
from openai import OpenAI
from dotenv import load_dotenv
import re
import bcrypt
from twilio.rest import Client
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import time as time_module
import decimal

# Simple in-memory cache for common responses
response_cache = {}
CACHE_TTL = 300  # 5 minutes cache

load_dotenv()

# Initialize OpenAI client with error handling
try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    client = OpenAI(api_key=openai_api_key)
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    client = None

# Twilio configuration for WhatsApp notifications
try:
    from twilio.rest import Client
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')  # Format: whatsapp:+14155238886
    ADMIN_WHATSAPP_NUMBER = os.getenv('ADMIN_WHATSAPP_NUMBER')  # Format: whatsapp:+1234567890
    
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        WHATSAPP_ENABLED = True
    else:
        WHATSAPP_ENABLED = False
        print("Warning: Twilio credentials not found. WhatsApp notifications disabled.")
except ImportError:
    WHATSAPP_ENABLED = False
    print("Warning: Twilio not installed. WhatsApp notifications disabled.")

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Custom JSON provider to handle datetime and time objects
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

app.json = CustomJSONProvider(app)

# Configure PostgreSQL database
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)

def get_quick_response(message):
    """Get instant responses for common questions without using LLM"""
    message_lower = message.lower().strip()
    
    # Fast responses for common questions
    quick_responses = {
        'hello': "Hello! Welcome to Dr. Venky Pet Clinic! 🐾 How can I help you today?",
        'hi': "Hi there! Welcome to Dr. Venky Pet Clinic! 🐾 How can I assist you?",
        'hours': "🕒 **Clinic Hours**: Monday-Saturday, 9 AM - 6 PM\n\nWe're closed on Sundays. For emergencies, please call our emergency line.",
        'services': "🏥 **Our Services**:\n• General health checkups\n• Vaccinations\n• Surgery\n• Emergency care\n• Dental care\n• Grooming\n• Pet boarding",
        'location': "📍 We're located at Dr. Venky Pet Clinic. Please call us for exact directions and parking information.",
        'price': "💰 For pricing information, please call us or visit in person. Costs vary based on your pet's needs.",
        'emergency': "🚨 **Emergency**: If this is a pet emergency, please call us immediately or visit the nearest emergency vet clinic!"
    }
    
    # Check for exact matches or partial matches
    for key, response in quick_responses.items():
        if key in message_lower or message_lower == key:
            return response
    
    # Check for greeting patterns
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return "Hello! Welcome to Dr. Venky Pet Clinic! 🐾 How can I help you and your pet today?"
    
    return None

def get_cached_response(message):
    """Check if we have a cached response for similar messages"""
    message_hash = hashlib.md5(message.lower().strip().encode()).hexdigest()
    current_time = time_module.time()
    
    if message_hash in response_cache:
        cached_data = response_cache[message_hash]
        if current_time - cached_data['timestamp'] < CACHE_TTL:
            return cached_data['response']
        else:
            # Clean expired cache
            del response_cache[message_hash]
    return None

def cache_response(message, response):
    """Cache a response for future use"""
    message_hash = hashlib.md5(message.lower().strip().encode()).hexdigest()
    response_cache[message_hash] = {
        'response': response,
        'timestamp': time_module.time()
    }

def get_db_connection():
    """Get database connection using psycopg2 for raw SQL operations"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database - schema should already exist in Supabase"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Test connection
                cur.execute("SELECT 1")
                print("Database connection successful")
                
                # Check if tables exist
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('users', 'appointments')
                """)
                tables = cur.fetchall()
                table_names = [table['table_name'] for table in tables]
                
                if 'users' not in table_names or 'appointments' not in table_names:
                    print("Warning: Required tables not found. Please run the SQL schema in Supabase.")
                    print("Required tables: users, appointments")
                    print("Found tables:", table_names)
                else:
                    print("All required tables found in database")
                    
                # Insert initial test data if not exists (optional for development)
                try:
                    cur.execute("SELECT * FROM users WHERE username = %s", ('testuser',))
                    user = cur.fetchone()
                    if not user:
                        hashed_pw = bcrypt.hashpw('testpass'.encode(), bcrypt.gensalt()).decode()
                        cur.execute(
                            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                            ('testuser', 'test@example.com', hashed_pw, 'user')
                        )
                        print("Test user created")
                    
                    # Insert initial test appointment if not exists
                    cur.execute("SELECT * FROM appointments WHERE pet_name = %s", ('Buddy',))
                    appointment = cur.fetchone()
                    if not appointment:
                        cur.execute("SELECT id FROM users WHERE username = %s", ('testuser',))
                        user = cur.fetchone()
                        user_id = user['id'] if user else None
                        cur.execute("""
                            INSERT INTO appointments (user_id, name, pet_name, phone, date, time, service, notes, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (user_id, 'Test User', 'Buddy', '1234567890', '2025-07-27', '10:00', 'General Consultation', 'First visit', 'scheduled'))
                        print("Test appointment created")
                    
                    conn.commit()
                except Exception as e:
                    print(f"Warning: Could not insert initial data: {e}")
                    conn.rollback()
                    
    except Exception as e:
        print(f"Database initialization error: {e}")
        print("Please ensure your DATABASE_URL is correct and Supabase tables are created")

# Initialize database when the module is imported
try:
    init_db()
    print("Database initialized successfully")
except Exception as e:
    print(f"Database initialization error: {e}")

def send_whatsapp_notification(appointment_data):
    """Send WhatsApp notification to admin about new appointment"""
    if not WHATSAPP_ENABLED:
        print("WhatsApp notifications are disabled.")
        return False
    
    if not ADMIN_WHATSAPP_NUMBER or not TWILIO_WHATSAPP_NUMBER:
        print("WhatsApp numbers not configured properly.")
        return False
    
    try:
        # Safely get values with fallbacks for None/missing data
        apt_id = appointment_data.get('id', 'Unknown')
        name = appointment_data.get('name', 'Not provided') or 'Not provided'
        pet_name = appointment_data.get('pet_name', 'Not provided') or 'Not provided'
        phone = appointment_data.get('phone', 'Not provided') or 'Not provided'
        date = appointment_data.get('date', 'Not specified') or 'Not specified'
        time = appointment_data.get('time', 'Not specified') or 'Not specified'
        service = appointment_data.get('service', 'General consultation') or 'General consultation'
        notes = appointment_data.get('notes', '') or ''
        status = appointment_data.get('status', 'scheduled') or 'scheduled'
        created_at = appointment_data.get('created_at', 'Unknown') or 'Unknown'
        
        # Format the appointment message
        message = f"""🏥 NEW APPOINTMENT REQUEST 🏥

📋 Appointment Details:
• ID: #{apt_id}
• Pet Owner: {name}
• Pet Name: {pet_name}
• Phone: {phone}
• Date: {date}
• Time: {time}
• Service: {service}
• Notes: {notes}

✅ Status: {status}
🕒 Requested at: {created_at}

Please review and confirm this appointment in your admin panel."""

        # Send WhatsApp message using Twilio
        message_instance = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=ADMIN_WHATSAPP_NUMBER
        )
        
        print(f"WhatsApp notification sent successfully. Message SID: {message_instance.sid}")
        print(f"Message status: {message_instance.status}")
        print(f"To: {ADMIN_WHATSAPP_NUMBER}")
        print(f"From: {TWILIO_WHATSAPP_NUMBER}")
        return True
        
    except Exception as e:
        print(f"Error sending WhatsApp notification: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error details for debugging
        return False

def extract_appointment_info(message):
    """Extract appointment information from user message using AI with optimization"""
    try:
        if client is None:
            print("OpenAI client not available, using fallback appointment detection")
            # Enhanced fallback appointment detection
            if any(word in message.lower() for word in ['appointment', 'book', 'schedule']):
                return {"appointment": True, "name": "Not provided", "pet_name": "Not provided", 
                       "date": "2025-07-27", "time": "10:00", "service": "general checkup", "notes": message}
            return {"appointment": False}
            
        # Use faster gpt-3.5-turbo-0125 model with optimized settings
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",  # Faster variant
            messages=[
                {"role": "system", "content": """Extract appointment details from user messages. Respond ONLY with JSON.
If booking: {"appointment": true, "name": "owner name", "pet_name": "pet name", "phone": "phone if provided", "date": "YYYY-MM-DD", "time": "HH:MM", "service": "service type", "notes": "additional info"}
If not booking: {"appointment": false}

Examples:
"book appointment for dog Max tomorrow 2pm, John Smith" -> {"appointment": true, "name": "John Smith", "pet_name": "Max", "date": "2025-07-28", "time": "14:00", "service": "general checkup", "notes": ""}
"hello" -> {"appointment": false}"""},
                {"role": "user", "content": message}
            ],
            max_tokens=150,  # Limit tokens for faster response
            temperature=0.1,  # Lower temperature for consistency
            timeout=10  # 10 second timeout
        )
        
        result = response.choices[0].message.content.strip()
        return json.loads(result)
    except Exception as e:
        print(f"AI extraction error: {e}")
        # Enhanced fallback for common patterns
        message_lower = message.lower()
        if any(word in message_lower for word in ['appointment', 'book', 'schedule']):
            return {
                "appointment": True, 
                "name": "Not provided", 
                "pet_name": "Not provided", 
                "date": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'), 
                "time": "10:00", 
                "service": "General Consultation", 
                "notes": message
            }
        return {"appointment": False}

def generate_available_slots():
    """Generate available appointment slots for the next 7 days"""
    available_slots = []
    base_date = datetime.now().date() + timedelta(days=1)  # Start from tomorrow
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT date, time FROM appointments')
            appointments = cur.fetchall()
            booked = set((apt['date'], apt['time']) for apt in appointments)
    
    for i in range(7):  # Next 7 days
        current_date = base_date + timedelta(days=i)
        if current_date.weekday() < 6:  # Monday to Saturday (0-5)
            for hour in range(9, 18):  # 9 AM to 5 PM
                slot_time = f"{hour:02d}:00"
                if (current_date, slot_time) not in booked:
                    available_slots.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'time': slot_time,
                        'day': current_date.strftime('%A')
                    })
    
    return available_slots[:10]  # Return first 10 available slots

def is_admin():
    return session.get('user') and session['user'].get('role') == 'admin'

def is_logged_in():
    return 'user' in session

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')
    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username/email and password are required.'}), 400
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT * FROM users WHERE username = %s OR email = %s',
                (username_or_email, username_or_email)
            )
            user = cur.fetchone()
            if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
                session['user'] = {
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
                return jsonify({'success': True, 'role': user['role'], 'username': user['username']})
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Username, email, and password are required.'}), 400
    if role == 'admin' and (not is_logged_in() or not is_admin()):
        return jsonify({'success': False, 'message': 'Only admin can create admin users.'}), 403
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)',
                    (username, email, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), role)
                )
                conn.commit()
                return jsonify({'success': True}), 201
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'message': 'User already exists.'}), 409
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': f'Unexpected error: {str(e)}'}), 500

@app.route('/user', methods=['GET'])
def get_user():
    if 'user' in session:
        return jsonify({'logged_in': True, 'user': session['user']})
    return jsonify({'logged_in': False})

@app.route('/admin.html')
def serve_admin():
    if not is_logged_in() or not is_admin():
        return redirect('/login.html')
    return render_template('admin.html')

@app.route('/login.html')
def serve_login():
    return render_template('login.html')

@app.route('/profile.html')
def serve_profile():
    return render_template('profile.html')

@app.route('/')
def serve_root():
    return render_template('index.html')

@app.route('/index.html')
def serve_index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'reply': "Please enter a message."}), 400
    
    # First, check for instant quick responses
    quick_reply = get_quick_response(user_message)
    if quick_reply:
        print(f"Quick response for: {user_message}")
        return jsonify({'reply': quick_reply})
    
    # Check cache for non-appointment messages
    if not any(word in user_message.lower() for word in ['appointment', 'book', 'schedule']):
        cached_reply = get_cached_response(user_message)
        if cached_reply:
            print(f"Cache hit for: {user_message[:50]}...")
            return jsonify({'reply': cached_reply})
    
    appointment_info = extract_appointment_info(user_message)
    if appointment_info.get('appointment'):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'INSERT INTO appointments (name, pet_name, phone, date, time, service, notes, status, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                        (
                            appointment_info.get('name', 'Not provided'),
                            appointment_info.get('pet_name', 'Not provided'),
                            appointment_info.get('phone', 'Not provided'),
                            appointment_info.get('date'),
                            appointment_info.get('time'),
                            appointment_info.get('service', 'General consultation'),
                            appointment_info.get('notes', ''),
                            'scheduled',
                            datetime.now().isoformat()
                        )
                    )
                    apt_id = cur.fetchone()['id']
                    conn.commit()
                    
                    cur.execute('SELECT * FROM appointments WHERE id = %s', (apt_id,))
                    new_appointment = cur.fetchone()
                    notification_sent = send_whatsapp_notification(dict(new_appointment))
                    notification_status = "✅ Admin notified via WhatsApp" if notification_sent else "⚠️ Admin notification failed"
                    reply = f"""✅ Appointment booked successfully!\n\n📋 **Appointment Details:**\n- **ID:** #{apt_id}\n- **Pet Owner:** {new_appointment['name']}\n- **Pet Name:** {new_appointment['pet_name']}\n- **Date:** {new_appointment['date']}\n- **Time:** {new_appointment['time']}\n- **Service:** {new_appointment['service']}\n\n📞 We'll call you if we need to confirm any details.\n{notification_status}\nThank you for choosing Dr. Venky Pet Clinic!"""
        except Exception as e:
            print("Appointment booking error:", str(e))
            return jsonify({'reply': f"Sorry, there was an error booking your appointment: {str(e)}. Please try again or call us directly."}), 500
    else:
        # Regular chat - check if asking about appointments or availability
        if any(word in user_message.lower() for word in ['appointment', 'book', 'schedule', 'available', 'slots']):
            available_slots = generate_available_slots()
            if available_slots:
                slots_text = "\n".join([f"• {slot['day']}, {slot['date']} at {slot['time']}" for slot in available_slots[:5]])
                reply = f"""📅 **Available Appointment Slots:**

{slots_text}

To book an appointment, please provide:
- Your name
- Pet's name  
- Preferred date and time
- Type of service needed

Example: "I want to book an appointment for my dog Max tomorrow at 2pm, my name is John Smith"
                """
            else:
                reply = "Sorry, no slots available in the next week. Please call us directly to schedule."
        else:
            # Regular veterinary chat with optimizations
            try:
                if client is None:
                    reply = """Hello! Welcome to Dr. Venky Pet Clinic. 
                    
I'm here to help with your pet care needs. Our services include:
- General health checkups
- Vaccinations  
- Surgery
- Emergency care
- Dental care
- Grooming
- Pet boarding

Clinic hours: Monday-Saturday, 9 AM - 6 PM

For appointments, please provide your name, pet's name, and preferred date/time."""
                else:
                    # Use faster model and optimized settings
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",  # Faster variant
                        messages=[
                            {"role": "system", "content": """You are Dr. Venky Pet Clinic assistant. Answer pet care questions briefly and professionally.

Services: General checkups, Vaccinations, Surgery, Emergency care, Dental care, Grooming, Pet boarding
Hours: Mon-Sat, 9 AM - 6 PM

For appointments: Ask for name, pet name, preferred date/time."""},
                            {"role": "user", "content": user_message}
                        ],
                        max_tokens=200,  # Limit response length
                        temperature=0.3,  # Lower for consistency
                        timeout=8  # 8 second timeout
                    )
                    reply = response.choices[0].message.content.strip()
                    
                    # Cache the response for future use
                    cache_response(user_message, reply)
            except Exception as e:
                print("OpenAI API error:", str(e))
                reply = "Sorry, I couldn't process your request right now. Please try again or call us directly."
    
    print("Reply:", reply[:100] + "..." if len(reply) > 100 else reply)
    return jsonify({'reply': reply})

@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments - for clinic admin"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT * FROM appointments ORDER BY created_at DESC')
                appointments = cur.fetchall()
                appointments_list = []
                for apt in appointments:
                    apt_dict = dict(apt)
                    # Convert problematic types to strings
                    for key, value in apt_dict.items():
                        if isinstance(value, time):
                            apt_dict[key] = value.strftime('%H:%M:%S')
                        elif isinstance(value, datetime):
                            apt_dict[key] = value.isoformat()
                        elif isinstance(value, date):
                            apt_dict[key] = value.isoformat()
                    appointments_list.append(apt_dict)
                return jsonify({'appointments': appointments_list, 'total': len(appointments_list)})
    except Exception as e:
        print(f"Error in get_appointments: {e}")
        return jsonify({'error': str(e), 'appointments': [], 'total': 0}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Test database connection
                cur.execute('SELECT 1')
                cur.fetchone()
                
                # Check if tables exist
                cur.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('users', 'appointments')
                """)
                tables = cur.fetchall()
                table_names = [table['table_name'] for table in tables]
                
                return jsonify({
                    'status': 'healthy',
                    'database': 'connected',
                    'tables': table_names,
                    'timestamp': datetime.now().isoformat()
                })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/appointments/<int:apt_id>', methods=['PUT'])
def update_appointment(apt_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    with get_db_connection() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute('UPDATE appointments SET status = %s, updated_at = %s WHERE id = %s',
                           (status, datetime.now().isoformat(), apt_id))
                conn.commit()
                if cur.rowcount:
                    return jsonify({'message': 'Appointment updated successfully'})
                else:
                    return jsonify({'error': 'Appointment not found'}), 404
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/performance', methods=['GET'])
def performance_stats():
    """Get performance statistics"""
    return jsonify({
        'cache_size': len(response_cache),
        'cache_items': list(response_cache.keys()),
        'optimizations': [
            'Quick pattern responses for common questions',
            'LLM response caching (5 min TTL)',
            'Faster GPT-3.5-turbo-0125 model',
            'Reduced token limits',
            'Request timeouts',
            'Lower temperature for consistency'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test-whatsapp', methods=['POST'])
def test_whatsapp():
    """Test WhatsApp notification functionality"""
    try:
        # Test data
        test_appointment = {
            'id': 999,
            'name': 'Test User',
            'pet_name': 'Test Pet',
            'phone': '555-TEST',
            'date': '2025-07-28',
            'time': '15:00',
            'service': 'Test Service',
            'notes': 'This is a test message',
            'status': 'test',
            'created_at': datetime.now().isoformat()
        }
        
        # Check configuration
        config_status = {
            'whatsapp_enabled': WHATSAPP_ENABLED,
            'twilio_account_sid': 'SET' if TWILIO_ACCOUNT_SID else 'NOT SET',
            'twilio_auth_token': 'SET' if TWILIO_AUTH_TOKEN else 'NOT SET',
            'twilio_whatsapp_number': TWILIO_WHATSAPP_NUMBER if TWILIO_WHATSAPP_NUMBER else 'NOT SET',
            'admin_whatsapp_number': ADMIN_WHATSAPP_NUMBER if ADMIN_WHATSAPP_NUMBER else 'NOT SET'
        }
        
        # Try to send test message
        if WHATSAPP_ENABLED:
            result = send_whatsapp_notification(test_appointment)
            return jsonify({
                'success': result,
                'config': config_status,
                'message': 'Test WhatsApp notification attempted',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'config': config_status,
                'message': 'WhatsApp is disabled',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/debug', methods=['GET'])
def debug_environment():
    """Debug endpoint to check environment variables and configuration"""
    try:
        # Check critical environment variables (safely)
        env_status = {}
        required_vars = [
            'DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_ANON_KEY', 
            'SUPABASE_SERVICE_ROLE_KEY', 'OPENAI_API_KEY', 
            'TWILIO_ACCOUNT_SID', 'SECRET_KEY', 'FLASK_ENV'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Show only first/last few characters for security
                if len(value) > 10:
                    display_value = value[:5] + "..." + value[-3:]
                else:
                    display_value = "***"
                env_status[var] = f"SET ({display_value})"
            else:
                env_status[var] = "NOT SET"
        
        # Test database connection
        db_status = "unknown"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT 1')
                    cur.fetchone()
            db_status = "connected"
        except Exception as e:
            db_status = f"failed: {str(e)[:100]}"
        
        return jsonify({
            'platform': 'render' if os.getenv('RENDER') else 'local',
            'environment_variables': env_status,
            'database_status': db_status,
            'python_version': os.sys.version,
            'working_directory': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 3001))
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)