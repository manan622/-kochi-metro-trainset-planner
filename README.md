# Kochi Metro Trainset Induction Planner

A comprehensive web application for planning nightly trainset induction operations at Kochi Metro. This system combines dummy authentication with role-based portals and intelligent induction planning logic to help operations teams make data-driven decisions about trainset deployment.

## 🚆 Overview

Every night, Kochi Metro must decide which of its 25 trainsets should:
- **Enter revenue service** (Fit)
- **Remain on standby** (Standby)  
- **Stay in Inspection Bay Line (IBL)** for maintenance (Unfit)

This decision depends on six interdependent variables:
1. **Fitness Certificates** (Rolling-Stock, Signalling, Telecom)
2. **Job-Card Status** (open/closed from IBM Maximo exports)
3. **Branding Priorities** (contractual exterior wrap commitments)
4. **Mileage Balancing** (kilometre equalisation)
5. **Cleaning & Detailing Slots** (bay/manpower constraints)
6. **Stabling Geometry** (minimise shunting and turnout time)

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **FastAPI** web framework with automatic API documentation
- **SQLAlchemy ORM** with Alembic migrations
- **PostgreSQL** database with comprehensive trainset models
- **JWT-based authentication** with role-based access control
- **Rule-based induction planner** with explainable reasoning
- **CSV import utilities** for data seeding

### Frontend (React + Tailwind CSS)
- **React 18** with modern hooks and context
- **React Router** for role-based navigation
- **Tailwind CSS** for responsive design
- **Axios** for API communication
- **Role-based portals** for different user types
- **Interactive dashboards** with real-time data

### Infrastructure
- **Docker Compose** for local development
- **PostgreSQL** database container
- **Nginx** reverse proxy for production
- **Alembic** database migrations

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd kochi-metro-induction-planner
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

4. **Seed sample data:**
   ```bash
   docker-compose exec backend python -c "from app.utils.csv_importer import generate_sample_data_command; generate_sample_data_command()"
   ```

### Option 2: Local Development

1. **Set up backend:**
   ```bash
   cd backend
   cp .env.example .env
   pip install -r requirements.txt
   
   # Start PostgreSQL (using Docker)
   docker run -d --name postgres -e POSTGRES_DB=kochi_metro_db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15
   
   # Run migrations
   alembic upgrade head
   
   # Generate sample data
   python -c "from app.utils.csv_importer import generate_sample_data_command; generate_sample_data_command()"
   
   # Start backend
   uvicorn main:app --reload
   ```

2. **Set up frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 👥 Demo Users

The system includes three demo users for testing different roles:

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | Management | Full system access, strategic overview |
| `inspector` | `inspect123` | Inspection | Technical assessment, maintenance planning |
| `worker` | `work123` | Worker | Daily tasks, operational assignments |

## 🎯 Key Features

### 1. Role-Based Access Control
- **Management Portal**: Strategic overview, fleet statistics, operational insights
- **Inspection Portal**: Technical assessment, maintenance planning, trainset evaluation
- **Worker Portal**: Daily task assignments, priority work items, operational tasks

### 2. Intelligent Induction Planning
- **Rule-based decision engine** with explainable reasoning
- **Multi-criteria evaluation** considering all operational factors
- **Conflict detection** and alert generation
- **Priority-based recommendations** for maintenance and operations

### 3. Comprehensive Trainset Management
- **Detailed trainset profiles** with complete operational history
- **Real-time status tracking** with reasoning explanations
- **Interactive fleet dashboard** with filtering and search
- **Expandable detail views** with all related data

### 4. Data Integration
- **CSV import utilities** for external system integration
- **Flexible data models** supporting complex operational requirements
- **Historical tracking** of all changes and decisions
- **Audit trails** for compliance and analysis

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Current user info

### Trainset Operations
- `POST /api/induction/plan` - Generate induction plan
- `GET /api/fleet/status` - Fleet status overview
- `GET /api/trainsets` - List all trainsets
- `GET /api/trainsets/{id}` - Trainset details
- `GET /api/trainsets/{id}/evaluation` - Detailed evaluation

## 🗂️ Project Structure

```
kochi-metro-induction-planner/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic
│   │   ├── utils/             # Utilities and helpers
│   │   └── schemas.py         # Pydantic schemas
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend container
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   ├── utils/             # Frontend utilities
│   │   └── App.js             # Main application
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── Dockerfile             # Frontend container
├── docker-compose.yml         # Development environment
├── README.md                  # This file
└── docs/                      # Additional documentation
```

## 🔧 Configuration

### Environment Variables (Backend)

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/kochi_metro_db

# JWT Configuration  
SECRET_KEY=your-secret-key-here-please-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
ENVIRONMENT=development

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Environment Variables (Frontend)

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Data Model

### Core Entities
- **Trainset**: Main operational unit with status and reasoning
- **FitnessCertificate**: Rolling-Stock, Signalling, and Telecom certificates
- **JobCard**: Maintenance tasks and work orders
- **BrandingPriority**: Contractual branding commitments
- **MileageRecord**: Daily operational mileage tracking
- **CleaningSlot**: Scheduled cleaning and detailing
- **StablingBay**: Physical stabling locations and capacity

### Decision Logic
The induction planner evaluates each trainset based on:
1. **Fitness certificate validity** (expired = unfit)
2. **Open job cards** (critical maintenance = unfit)
3. **Branding priority** (high priority = fit)
4. **Mileage balancing** (prefer even distribution)
5. **Cleaning schedule** (scheduled cleaning considered)
6. **Stabling bay availability** (capacity constraints)

## 🔒 Security Considerations

⚠️ **IMPORTANT**: This application uses dummy authentication for demonstration purposes only.

### Current Security Implementation
- JWT tokens with configurable expiration
- Role-based access control
- CORS configuration
- Basic input validation

### Production Security Checklist
- [ ] Replace dummy authentication with proper identity provider
- [ ] Implement proper password hashing and validation
- [ ] Add rate limiting and request throttling
- [ ] Enable HTTPS/TLS encryption
- [ ] Implement proper session management
- [ ] Add comprehensive input validation and sanitization
- [ ] Set up proper logging and monitoring
- [ ] Configure firewall and network security
- [ ] Implement backup and disaster recovery
- [ ] Add security headers and CSP policies

## 🚨 Known Limitations

1. **Authentication**: Uses hardcoded dummy users - not suitable for production
2. **Data Persistence**: Sample data is generated randomly on each startup
3. **Real-time Updates**: No WebSocket implementation for live updates
4. **Performance**: Not optimized for large-scale deployments
5. **Error Handling**: Basic error handling - needs improvement for production
6. **Testing**: Limited test coverage - needs comprehensive test suite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is developed for demonstration purposes. Please ensure proper licensing for production use.

## 🆘 Support

For questions or issues:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the console logs for error details
3. Verify environment variables and database connectivity
4. Ensure all services are running properly

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**Built with ❤️ for Kochi Metro Rail Limited**