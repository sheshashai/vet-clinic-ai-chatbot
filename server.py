import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import re
import bcrypt
from twilio.rest import Client
import sqlite3

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        return True
        
    except Exception as e:
        print(f"Error sending WhatsApp notification: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error details for debugging
        return False

def extract_appointment_info(message):
    """Extract appointment information from user message using AI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
You are an appointment extraction assistant. Extract appointment details from user messages and respond ONLY with a JSON object.
If the user wants to book an appointment, extract:
- name: pet owner's name
- pet_name: pet's name
- phone: phone number (if provided)
- date: preferred date (format: YYYY-MM-DD, if not specific use next available weekday)
- time: preferred time (format: HH:MM, if not specific use 10:00)
- service: type of service needed
- notes: any additional information

If it's not an appointment request, respond with: {"appointment": false}

Examples:
"I want to book appointment for my dog Max tomorrow at 2pm, my name is John" -> 
{"appointment": true, "name": "John", "pet_name": "Max", "date": "2025-07-25", "time": "14:00", "service": "general checkup", "notes": ""}

"Hello" -> 
{"appointment": false}
                """},
                {"role": "user", "content": message}
            ]
        )
        
        result = response.choices[0].message.content.strip()
        return json.loads(result)
    except:
        return {"appointment": False}

def generate_available_slots():
    """Generate available appointment slots for the next 7 days"""
    available_slots = []
    base_date = datetime.now().date() + timedelta(days=1)  # Start from tomorrow
    with get_db_connection() as conn:
        appointments = conn.execute('SELECT date, time FROM appointments').fetchall()
        booked = set((apt['date'], apt['time']) for apt in appointments)
    for i in range(7):  # Next 7 days
        current_date = base_date + timedelta(days=i)
        if current_date.weekday() < 6:  # Monday to Saturday (0-5)
            for hour in range(9, 18):  # 9 AM to 5 PM
                slot_time = f"{hour:02d}:00"
                if (current_date.strftime('%Y-%m-%d'), slot_time) not in booked:
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

def init_db():
    with get_db_connection() as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          email TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL,
          role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS appointments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          name TEXT,
          pet_name TEXT NOT NULL,
          phone TEXT,
          date TEXT NOT NULL,
          time TEXT NOT NULL,
          service TEXT DEFAULT 'General Consultation',
          notes TEXT,
          status TEXT DEFAULT 'scheduled',
          created_at TEXT DEFAULT (datetime('now')),
          updated_at TEXT DEFAULT (datetime('now')),
          FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        ''')
        # Insert initial test user if not exists
        user = conn.execute("SELECT * FROM users WHERE username = ?", ('testuser',)).fetchone()
        if not user:
            import bcrypt
            hashed_pw = bcrypt.hashpw('testpass'.encode(), bcrypt.gensalt()).decode()
            conn.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                         ('testuser', 'test@example.com', hashed_pw, 'user'))
        # Insert initial test appointment if not exists
        appointment = conn.execute("SELECT * FROM appointments WHERE pet_name = ?", ('Buddy',)).fetchone()
        if not appointment:
            user_id = conn.execute("SELECT id FROM users WHERE username = ?", ('testuser',)).fetchone()
            user_id = user_id['id'] if user_id else None
            conn.execute("""
                INSERT INTO appointments (user_id, pet_name, phone, date, time, service, notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, 'Buddy', '1234567890', '2025-07-25', '10:00', 'General Consultation', 'First visit', 'scheduled'))
        conn.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')
    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username/email and password are required.'}), 400
    with get_db_connection() as conn:
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username_or_email, username_or_email)
        ).fetchone()
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
            conn.execute(
                'INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                (username, email, bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(), role)
            )
            conn.commit()
            return jsonify({'success': True}), 201
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'User already exists.'}), 409
        except Exception as e:
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
    appointment_info = extract_appointment_info(user_message)
    if appointment_info.get('appointment'):
        try:
            with get_db_connection() as conn:
                cur = conn.execute(
                    'INSERT INTO appointments (name, pet_name, phone, date, time, service, notes, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
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
                apt_id = cur.lastrowid
                conn.commit()
                new_appointment = conn.execute('SELECT * FROM appointments WHERE id = ?', (apt_id,)).fetchone()
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
            # Regular veterinary chat
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are a helpful assistant for Dr. Venky Pet Clinic. 
                        Answer questions about pet care, veterinary services, pet health, vaccinations, and general pet advice. 
                        Be friendly and professional. If users ask about appointments, guide them to provide their details for booking.
                        
                        Services offered:
                        - General health checkups
                        - Vaccinations
                        - Surgery
                        - Emergency care
                        - Dental care
                        - Grooming
                        - Pet boarding
                        
                        Clinic hours: Monday-Saturday, 9 AM - 6 PM"""},
                        {"role": "user", "content": user_message}
                    ]
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                print("OpenAI API error:", str(e))
                reply = "Sorry, I couldn't process your request right now."
    
    print("Reply:", reply)
    return jsonify({'reply': reply})

@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments - for clinic admin"""
    with get_db_connection() as conn:
        appointments = conn.execute('SELECT * FROM appointments').fetchall()
        appointments_list = [dict(apt) for apt in appointments]
        return jsonify({'appointments': appointments_list, 'total': len(appointments_list)})

@app.route('/appointments/<int:apt_id>', methods=['PUT'])
def update_appointment(apt_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({'error': 'Status is required'}), 400
    with get_db_connection() as conn:
        try:
            result = conn.execute('UPDATE appointments SET status = ?, updated_at = ? WHERE id = ?',
                                 (status, datetime.now().isoformat(), apt_id))
            conn.commit()
            if result.rowcount:
                return jsonify({'message': 'Appointment updated successfully'})
            else:
                return jsonify({'error': 'Appointment not found'}), 404
        except Exception as e:
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=3001, debug=True)