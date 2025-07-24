# Dr. Venky Pet Clinic Chatbot 🐾

A comprehensive veterinary clinic management system featuring an AI-powered chatbot, appointment scheduling, and admin dashboard. Built with Flask, OpenAI API, and modern web technologies.

## 🌟 Features

### 🤖 AI Chatbot
- Intelligent conversation system powered by OpenAI GPT
- Pet health consultation and advice
- Natural language processing for veterinary queries
- Context-aware responses for pet care

### 📅 Appointment Management
- Online appointment booking system
- Real-time availability checking
- Appointment confirmation and management
- Status tracking (scheduled, confirmed, completed, cancelled)

### 📱 WhatsApp Notifications
- Automatic WhatsApp notifications to admin for new appointments
- Twilio integration for reliable messaging
- Real-time appointment alerts

### 👨‍💼 Admin Dashboard
- Comprehensive appointment management
- User management system
- Appointment status updates
- Analytics and reporting

### 🔐 User Authentication
- Secure user registration and login
- Password hashing with bcrypt
- Session management
- User profile management

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **AI Integration**: OpenAI API
- **Messaging**: Twilio WhatsApp API
- **Authentication**: bcrypt
- **Data Storage**: JSON files (easily upgradeable to database)
- **Styling**: Modern CSS with glassmorphism design

## 📋 Prerequisites

- Python 3.7+
- OpenAI API key
- Twilio account (for WhatsApp notifications)
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
