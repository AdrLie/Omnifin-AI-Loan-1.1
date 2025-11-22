# Omnifin - AI-Powered Loans & Insurance Platform

## Overview

Omnifin is a comprehensive SaaS platform that leverages AI to provide fast loans and insurance services through conversational interfaces. The platform supports both text-based chat and voice interactions, with a complete user management system and analytics dashboard.

## Features

### Core Functionality
- **AI-Powered Chat Interface**: Text-based conversations with AI assistant
- **Voice Chat**: Speech-to-text and text-to-speech capabilities
- **User Management**: Role-based access control with 4 user levels
- **Analytics Dashboard**: Real-time metrics and reporting
- **Knowledge Base**: AI training data and prompt management
- **File Upload**: Drag-and-drop file management system

### User Roles
1. **Simple User**: Basic platform access
2. **Super User**: Additional permissions via dashboard
3. **Admin User**: Create/manage users within their group
4. **SuperAdmin**: Full platform control

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **Database**: PostgreSQL (Primary + Knowledge Bank)
- **API**: Django REST Framework
- **Authentication**: Token-based authentication
- **Task Queue**: Celery with Redis
- **File Storage**: Local with cloud-ready architecture

### Frontend
- **Framework**: React 18 with React Native Web
- **UI Library**: Material-UI (MUI)
- **State Management**: Context API
- **Routing**: React Router DOM
- **HTTP Client**: Axios

### External Services
- **AI Models**: OpenAI GPT, ElevenLabs (voice)
- **Cache**: Redis
- **Monitoring**: Built-in analytics and logging

## Project Structure

```
/mnt/okcomputer/output/
├── backend/                    # Django backend application
│   ├── omnifin/               # Main Django project
│   ├── authentication/        # User authentication app
│   ├── core/                  # Core functionality app
│   ├── order/                 # Order and conversation management
│   ├── knowledge/             # Knowledge base and AI training
│   ├── analytics/             # Analytics and reporting
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts
│   │   ├── services/          # API services
│   │   └── hooks/             # Custom hooks
│   ├── public/                # Static assets
│   └── package.json           # Node.js dependencies
├── requirements.md            # Requirements documentation
├── workflow.md               # Workflow documentation
├── database_schema.md        # Database schema documentation
├── workflow_diagram.png      # Visual workflow diagram
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### Backend Setup

1. **Create Virtual Environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create a `.env` file in the backend directory:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=omnifin_primary
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
KNOWLEDGE_DB_NAME=omnifin_knowledge
KNOWLEDGE_DB_USER=postgres
KNOWLEDGE_DB_PASSWORD=your-db-password
KNOWLEDGE_DB_HOST=localhost
KNOWLEDGE_DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
REDIS_URL=redis://127.0.0.1:6379/1
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

4. **Setup Database**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --database=knowledge
```

5. **Create Superuser**
```bash
python manage.py createsuperuser
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Configure Environment**
Create a `.env` file in the frontend directory:
```bash
REACT_APP_API_URL=http://localhost:8000/api
```

3. **Start Development Server**
```bash
npm start
```

### Running the Application

1. **Start Django Development Server**
```bash
cd backend
python manage.py runserver
```

2. **Start Celery Worker (Optional)**
```bash
celery -A omnifin worker --loglevel=info
```

3. **Start Frontend Development Server**
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/me/` - Get current user
- `PUT /api/auth/profile/update/` - Update user profile

### Chat Endpoints
- `POST /api/order/chat/start/` - Start new conversation
- `POST /api/order/chat/{id}/message/` - Send message
- `GET /api/order/chat/{id}/history/` - Get chat history

### Voice Chat Endpoints
- `POST /api/order/voice-chat/start/` - Start voice conversation
- `POST /api/order/voice-chat/{id}/message/` - Send voice message

### Admin Endpoints
- `GET /api/auth/users/` - List users
- `POST /api/auth/users/` - Create user
- `PUT /api/auth/users/{id}/` - Update user
- `DELETE /api/auth/users/{id}/` - Delete user

## Configuration

### API Keys Setup
1. **OpenAI API**: Get API key from [OpenAI Platform](https://platform.openai.com/)
2. **ElevenLabs API**: Get API key from [ElevenLabs](https://elevenlabs.io/)

### Database Configuration
The platform uses two PostgreSQL databases:
- **Primary Database**: User management, orders, analytics
- **Knowledge Bank**: AI training data, prompts, knowledge entries

### Redis Configuration
Redis is used for:
- Celery task queue
- Cache storage
- Session management

## Development

### Adding New Features
1. **Backend**: Create models, views, serializers, and URLs in appropriate apps
2. **Frontend**: Create components and pages, add routing
3. **API Integration**: Update service files for API communication

### Testing
- Backend: Django test framework
- Frontend: React Testing Library
- Integration: Manual testing through UI

## Deployment

### Production Setup
1. **Environment Variables**: Set production values in environment
2. **Database**: Use production PostgreSQL instance
3. **Static Files**: Collect static files with `python manage.py collectstatic`
4. **Security**: Enable HTTPS, configure firewalls
5. **Monitoring**: Set up logging and monitoring

### Docker Deployment
Docker configuration files are available for easy deployment:
- `Dockerfile` for backend
- `docker-compose.yml` for full stack

## Monitoring & Maintenance

### Health Checks
- System health endpoint: `/api/core/system/health/`
- Database connectivity
- API response times
- Error rates

### Logging
- Application logs in `backend/logs/`
- Error tracking and monitoring
- User activity tracking

### Backup Strategy
- Regular database backups
- File storage backups
- Configuration backups

## Security Considerations

### Authentication
- Token-based authentication
- Password hashing with Django's built-in system
- Session management

### Authorization
- Role-based access control
- Permission checking at API level
- Resource ownership validation

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

## Support & Troubleshooting

### Common Issues
1. **Database Connection**: Check PostgreSQL service and credentials
2. **Redis Connection**: Ensure Redis is running and accessible
3. **API Key Issues**: Verify OpenAI and ElevenLabs API keys
4. **CORS Issues**: Check frontend API URL configuration

### Getting Help
- Check application logs for error details
- Verify environment variable configuration
- Test individual components (database, Redis, etc.)

## License

This project is proprietary software developed for Omnifin platform.

## Contributing

Please follow the established coding standards and submit pull requests for review.

---

For more detailed information, refer to the individual documentation files:
- `requirements.md` - Detailed requirements specification
- `workflow.md` - System workflow and architecture
- `database_schema.md` - Complete database design

For technical support, please contact the development team.