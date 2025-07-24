import os
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import re
import bcrypt
from twilio.rest import Client

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

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# Simple in-memory storage for appointments (in production, use a database)
appointments = []

def save_appointments():
    """Save appointments to a JSON file"""
    with open('appointments.json', 'w') as f:
        json.dump(appointments, f, indent=2, default=str)

def load_appointments():
    """Load appointments from JSON file"""
    global appointments
    try:
        with open('appointments.json', 'r') as f:
            appointments = json.load(f)
    except FileNotFoundError:
        appointments = []

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
    
    for i in range(7):  # Next 7 days
        current_date = base_date + timedelta(days=i)
        if current_date.weekday() < 6:  # Monday to Saturday (0-5)
            for hour in range(9, 18):  # 9 AM to 5 PM
                slot_time = f"{hour:02d}:00"
                # Check if slot is already booked
                is_booked = any(
                    apt['date'] == current_date.strftime('%Y-%m-%d') and 
                    apt['time'] == slot_time 
                    for apt in appointments
                )
                if not is_booked:
                    available_slots.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'time': slot_time,
                        'day': current_date.strftime('%A')
                    })
    
    return available_slots[:10]  # Return first 10 available slots

def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

def get_user_by_username_or_email(username_or_email):
    users = load_users()
    for user in users:
        if user['username'] == username_or_email or user['email'] == username_or_email:
            return user
    return None

def is_admin():
    return session.get('user') and session['user'].get('role') == 'admin'

def is_logged_in():
    return 'user' in session

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Login attempt received:", data)  # Debug log
    username_or_email = data.get('username')
    password = data.get('password')
    print(f"Looking for user: {username_or_email}")  # Debug log
    
    user = get_user_by_username_or_email(username_or_email)
    print(f"User found: {user is not None}")  # Debug log
    
    if user:
        print(f"Checking password for user: {user['username']}")  # Debug log
        try:
            password_match = bcrypt.checkpw(password.encode(), user['password'].encode())
            print(f"Password match: {password_match}")  # Debug log
            
            if password_match:
                session['user'] = {
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
                print(f"Login successful for user: {user['username']}, role: {user['role']}")  # Debug log
                return jsonify({'success': True, 'role': user['role'], 'username': user['username']})
            else:
                print("Password does not match")  # Debug log
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        except Exception as e:
            print(f"Password check error: {e}")  # Debug log
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    else:
        print("User not found")  # Debug log
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Registration attempt:", data)  # Debug logging
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    
    print(f"Attempting to register user: {username}, email: {email}, role: {role}")
    
    if role == 'admin' and (not is_logged_in() or not is_admin()):
        print("Admin role requested but user not authorized")
        return jsonify({'success': False, 'message': 'Only admin can create admin users.'}), 403
    
    if get_user_by_username_or_email(username) or get_user_by_username_or_email(email):
        print("User already exists")
        return jsonify({'success': False, 'message': 'User already exists.'}), 409
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users = load_users()
    new_user = {
        'username': username,
        'email': email,
        'password': hashed_pw,
        'role': role
    }
    users.append(new_user)
    print(f"Adding user to list: {new_user['username']}")
    save_users(users)
    print(f"Users saved. Total users now: {len(users)}")
    return jsonify({'success': True})

@app.route('/user', methods=['GET'])
def get_user():
    if 'user' in session:
        return jsonify({'logged_in': True, 'user': session['user']})
    return jsonify({'logged_in': False})

@app.route('/admin.html')
def serve_admin():
    if not is_logged_in() or not is_admin():
        return redirect('/login.html')
    return send_from_directory('.', 'admin.html')

@app.route('/login.html')
def serve_login():
    return send_from_directory('.', 'login.html')

@app.route('/profile.html')
def serve_profile():
    return send_from_directory('.', 'profile.html')

@app.route('/')
def serve_root():
    return send_from_directory('.', 'index.html')

@app.route('/index.html')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    print("User message:", user_message)
    
    if not user_message:
        return jsonify({'reply': "Please enter a message."})
    
    # Check if this is an appointment request
    appointment_info = extract_appointment_info(user_message)
    
    if appointment_info.get('appointment'):
        # This is an appointment request
        try:
            # Generate appointment ID
            apt_id = len(appointments) + 1
            
            # Create appointment object with safe fallbacks
            new_appointment = {
                'id': apt_id,
                'name': appointment_info.get('name', 'Not provided') or 'Not provided',
                'pet_name': appointment_info.get('pet_name', 'Not provided') or 'Not provided',
                'phone': appointment_info.get('phone', 'Not provided') or 'Not provided',
                'date': appointment_info.get('date') or 'Not specified',
                'time': appointment_info.get('time') or 'Not specified',
                'service': appointment_info.get('service', 'General consultation') or 'General consultation',
                'notes': appointment_info.get('notes', '') or '',
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }
            
            appointments.append(new_appointment)
            save_appointments()
            
            # Debug logging for notification
            print(f"Attempting to send WhatsApp notification for appointment #{apt_id}")
            print(f"Appointment data: {new_appointment}")
            
            # Send WhatsApp notification to admin
            notification_sent = send_whatsapp_notification(new_appointment)
            
            # Include notification status in response
            notification_status = "✅ Admin notified via WhatsApp" if notification_sent else "⚠️ Admin notification failed"
            print(f"Notification result: {notification_status}")
            
            reply = f"""✅ Appointment booked successfully!

📋 **Appointment Details:**
- **ID:** #{apt_id}
- **Pet Owner:** {new_appointment['name']}
- **Pet Name:** {new_appointment['pet_name']}
- **Date:** {new_appointment['date']}
- **Time:** {new_appointment['time']}
- **Service:** {new_appointment['service']}

📞 We'll call you if we need to confirm any details.
{notification_status}
Thank you for choosing Dr. Venky Pet Clinic!"""
            
        except Exception as e:
            print("Appointment booking error:", str(e))
            reply = "Sorry, there was an error booking your appointment. Please try again or call us directly."
    
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
    return jsonify({
        'appointments': appointments,
        'total': len(appointments)
    })

@app.route('/appointments/<int:apt_id>', methods=['PUT'])
def update_appointment(apt_id):
    """Update appointment status"""
    data = request.get_json()
    status = data.get('status', 'scheduled')
    
    for apt in appointments:
        if apt['id'] == apt_id:
            apt['status'] = status
            apt['updated_at'] = datetime.now().isoformat()
            save_appointments()
            return jsonify({'message': 'Appointment updated successfully'})
    
    return jsonify({'error': 'Appointment not found'}), 404

# Load existing appointments on startup
load_appointments()

if __name__ == '__main__':
    app.run(port=3001, debug=True)