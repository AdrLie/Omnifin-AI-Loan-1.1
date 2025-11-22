# Omnifin - AI-Enabled Loans & Insurance Platform
## Requirements Document

### 1. Project Overview
Omnifin is a comprehensive SaaS platform that leverages AI to provide fast loans and insurance services through conversational interfaces. The platform supports both text-based chat and voice interactions.

### 2. Core Functionality

#### 2.1 User Management System
- **User Roles & Permissions:**
  - Simple User: Basic platform usage, no admin access
  - Super User: Additional permissions assigned via dashboard
  - Admin User: Create/manage Simple & Super users within their group
  - SuperAdmin: Full platform control, create any user type

- **Authentication:**
  - One-factor authentication system
  - User registration and login
  - Session management
  - Password reset functionality

#### 2.2 AI-Powered Services
- **Text Chat Interface:**
  - LLM-powered chat for loan/insurance inquiries
  - Real-time conversation handling
  - API integration to external databases/CRMs
  - Order processing through conversational AI

- **Voice Chat Interface:**
  - STT (Speech-to-Text) integration
  - Voice capture via device microphone
  - TTS (Text-to-Speech) for responses
  - Real-time voice conversation handling

#### 2.3 Knowledge Management
- **Knowledge Bank:**
  - Group-specific knowledge databases
  - Admin-controlled content updates
  - AI training data storage
  - Prompt management system

### 3. Technical Requirements

#### 3.1 Backend (Django)
- **Framework:** Django 4.x
- **Database:** PostgreSQL
- **Key Apps:**
  - authentication: User management and auth
  - core: Platform core functionality
  - knowledge: Knowledge bank management
  - order: Order processing and management
  - analytics: Usage analytics and reporting

#### 3.2 Frontend (React Native + Web)
- **Framework:** React Native with React Native Web
- **UI Library:** Material-UI (MUI)
- **Styling:** CSS-in-JS with responsive design
- **State Management:** Context API/Redux

#### 3.3 Database Schema
- **Primary Database:** User management, orders, analytics
- **Knowledge Bank:** AI training data, prompts, group-specific content

### 4. Page Structure

#### 4.1 User Pages
1. **Login Page:** User authentication
2. **Chat Interface:** Text-based AI interaction
3. **Voice Chat:** Voice-based AI interaction
4. **Profile Page:** User profile management

#### 4.2 Admin Pages
5. **API Configuration:** LLM and external system API setup
6. **Prompt Management:** LLM prompt configuration
7. **Knowledge Bank:** Content management for AI
8. **User Management:** Create/edit users and permissions
9. **Analytics Dashboard:** Usage statistics and reporting

### 5. Features Detailed

#### 5.1 User Management & Moderation
- User list with roles and status
- Permission editing interface
- Content moderation tools
- Account suspension/banning
- Activity logging and monitoring

#### 5.2 Analytics Dashboard
- Interactive charts with Chart.js
- Real-time data updates
- User engagement metrics
- Traffic source analysis
- Exportable reports (CSV/PDF)
- Blog-style statistics (views, interactions)

#### 5.3 LLM Prompt Management
- Prompt categorization and listing
- Rich text editor for prompt creation
- Preview and testing environment
- Version control for prompt changes
- Search and filter functionality

#### 5.4 Image Upload System
- Drag-and-drop file upload
- Multiple file support
- Image preview with metadata
- File validation (JPG, PNG, GIF, WebP, SVG)
- 5MB size limit per image
- Progress indicators
- Mobile-responsive design

### 6. Design Requirements
- **Style:** Minimalist and modern
- **Colors:** Purple highlights with neutral base
- **Responsiveness:** Desktop and mobile optimization
- **Navigation:** Top menu bar with page links
- **Accessibility:** WCAG 2.1 compliance

### 7. Integration Requirements
- **LLM APIs:** OpenAI, Anthropic, or similar
- **Voice AI:** ElevenLabs or similar full-stack voice solution
- **External Systems:** CRM/ERP integration capabilities
- **Database APIs:** RESTful endpoints for all operations

### 8. Security Requirements
- **Authentication:** Secure session management
- **Authorization:** Role-based access control
- **Data Protection:** Encryption for sensitive data
- **API Security:** Token-based authentication
- **Input Validation:** SQL injection and XSS prevention

### 9. Performance Requirements
- **Response Time:** <3 seconds for API calls
- **Scalability:** Support for 1000+ concurrent users
- **Availability:** 99.9% uptime
- **Data Storage:** Efficient query optimization

### 10. Development Phases
1. Requirements gathering and documentation
2. Database design and setup
3. Backend API development
4. Frontend component creation
5. Integration and testing
6. Deployment and documentation

### 11. Success Criteria
- All user roles functional with proper permissions
- AI chat and voice interfaces operational
- Analytics dashboard with real-time data
- Secure authentication and authorization
- Responsive design across devices
- Complete API documentation
- Production-ready deployment configuration