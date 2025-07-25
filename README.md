# 🚀 Dr. Venky Pet Clinic AI Chatbot

A comprehensive veterinary clinic management system featuring an AI-powered chatbot, appointment scheduling, user authentication, and admin dashboard. Built with Flask, OpenAI API, and modern web technologies.

![Vet Clinic Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🤖 **AI-Powered Chatbot**
- Intelligent conversation system powered by OpenAI GPT
- Pet health consultation and veterinary advice
- Natural language processing for pet care queries
- Context-aware responses tailored for veterinary needs

### 📅 **Appointment Management**
- Online appointment booking with real-time availability
- Smart scheduling system with conflict prevention
- Appointment status tracking (scheduled, confirmed, completed, cancelled)
- Automated appointment confirmations

### 📱 **WhatsApp Integration**
- Instant WhatsApp notifications to admin for new appointments
- Twilio integration for reliable messaging
- Real-time appointment alerts and updates

### � **Secure Authentication**
- User registration and login system
- Password hashing with bcrypt for security
- Session management with Flask sessions
- User profile management

### �👨‍💼 **Admin Dashboard**
- Comprehensive appointment management interface
- User management and oversight
- Appointment analytics and reporting
- System health monitoring

## 🛠️ Technology Stack

- **Backend**: Python Flask 3.0+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: OpenAI GPT API
- **Messaging**: Twilio WhatsApp API
- **Database**: SQLite (production-ready, easily upgradeable)
- **Authentication**: bcrypt password hashing
- **Styling**: Modern CSS with glassmorphism design

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Twilio account (for WhatsApp notifications)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/sheshashai/vet-clinic-ai-chatbot.git
   cd vet-clinic-ai-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

5. **Initialize the database**
   ```bash
   python server.py
   # Database will be created automatically on first run
   ```

6. **Run the application**
   ```bash
   python server.py
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:3001`
   - Register a new account or use the login system

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
ADMIN_WHATSAPP_NUMBER=whatsapp:+1234567890

# Flask Configuration
SECRET_KEY=your_secret_key_for_sessions
```

## 🚀 Usage

### For Pet Owners
1. Register for an account on the login page
2. Book appointments through the scheduling system
3. Chat with the AI assistant for pet health advice
4. Manage your profile and appointment history

### For Administrators
1. Access the admin dashboard after logging in with admin credentials
2. Manage all appointments and user accounts
3. Monitor system activity and analytics
4. Receive real-time WhatsApp notifications for new appointments
- Web browser

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dr-venky-pet-clinic-chatbot.git
   cd dr-venky-pet-clinic-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ADMIN_WHATSAPP_NUMBER=whatsapp:+1234567890
   ```

4. **Run the application**
   ```bash
   python server.py
   ```

5. **Access the application**
   - Main chatbot: `http://localhost:5000`
   - Admin dashboard: `http://localhost:5000/admin.html`
   - User login: `http://localhost:5000/login.html`

## 📁 Project Structure

```
├── server.py              # Main Flask application
├── index.html             # Main chatbot interface
├── admin.html             # Admin dashboard
├── login.html             # User login page
├── profile.html           # User profile page
├── style.css              # Styling
├── requirements.txt       # Python dependencies
├── appointments.json      # Appointment data storage
├── users.json            # User data storage
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## 🎯 Usage

### For Pet Owners
1. Visit the main page and start chatting with the AI assistant
2. Ask questions about pet health, symptoms, or general care
3. Book appointments through the chat interface
4. Create an account to track your appointments
5. Manage your profile and appointment history

### For Clinic Staff
1. Access the admin dashboard (`/admin.html`)
2. View all incoming appointments
3. Update appointment statuses
4. Manage user accounts
5. Receive WhatsApp notifications for new bookings

## 🔧 Configuration

### OpenAI Integration
- Configure your OpenAI API key in the `.env` file
- Customize the chatbot's behavior by modifying the system prompts in `server.py`

### WhatsApp Notifications
- Set up a Twilio account
- Configure your Twilio credentials in the `.env` file
- Verify your WhatsApp sandbox number

### Styling Customization
- Modify `style.css` for custom branding
- Update color schemes and layouts as needed
- Responsive design works on all devices

## 🚀 Deployment

### Local Development
```bash
python server.py
```

### Production Deployment
1. Use a WSGI server like Gunicorn
2. Configure environment variables
3. Set up a reverse proxy (nginx)
4. Use a proper database instead of JSON files

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## 📊 API Endpoints

- `GET /` - Main chatbot interface
- `POST /chat` - Chat with AI assistant
- `POST /book_appointment` - Book new appointment
- `GET /appointments` - Get user appointments
- `POST /register` - User registration
- `POST /login` - User login
- `GET /admin.html` - Admin dashboard
- `POST /update_appointment_status` - Update appointment status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- OpenAI for the GPT API
- Twilio for WhatsApp integration
- Flask community for the excellent framework
- Font Awesome for icons
- Google Fonts for typography

## 📞 Support

For support, email sheshuboin@gmail.com or create an issue in this repository.

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL/MySQL)
- [ ] Email notifications
- [ ] Multi-language support
- [ ] Mobile app development
- [ ] Payment integration
- [ ] Appointment reminders
- [ ] Video consultation feature
- [ ] Medical records management

---

Made with ❤️ for pet lovers and their furry friends 🐕🐱
