# Cleaning Team Dashboard System - Complete Guide

## Overview
A comprehensive cleaning management system for metro train operations that includes:
- Separate cleaning team dashboard with authentication
- Camera access for photo capture after cleaning
- AI-powered photo evaluation using Google Gemini
- Team assignment tracking
- Integration with management dashboard

## System Components

### 1. Database Models
- **CleaningTeam**: Team information with unique IDs (CT-001, CT-002, etc.)
- **CleaningUser**: Cleaning staff with roles (Team Leader, Cleaner, Supervisor)
- **CleaningAssignment**: Train assignments to cleaning teams
- **CleaningPhotoEvaluation**: AI-evaluated photos with quality scores

### 2. AI Integration
- **Gemini AI Service**: Evaluates cleaning photos for quality assessment
- **API Key**: AIzaSyD66l2j_rcxVJAq6WkQEWURxXb7hkT7sDI (configured in system)
- **Evaluation Criteria**: Cleanliness, safety compliance, thoroughness

### 3. Authentication System
- Separate JWT authentication for cleaning teams
- Role-based access control
- Team-specific dashboards

## Getting Started

### 1. Setup Database
```bash
cd backend
python setup_cleaning_data.py
```

### 2. Start Backend Server
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start Frontend
```bash
cd frontend
npm start
```

### 4. Access Points
- **Management Dashboard**: http://localhost:3000/
- **Cleaning Dashboard**: http://localhost:3000/cleaning/login

## Demo Credentials

### Cleaning Team Login
- **Username**: cleaner1 | **Password**: password123 (Team Alpha - Cleaner)
- **Username**: cleaner2 | **Password**: password123 (Team Beta - Cleaner)
- **Username**: supervisor1 | **Password**: password123 (Rapid Response - Supervisor)

### Management Login (existing)
- **Username**: admin | **Password**: admin123

## How to Use the Cleaning System

### For Cleaning Teams:

1. **Login**
   - Go to `/cleaning/login`
   - Use demo credentials above
   - System authenticates and shows team-specific dashboard

2. **View Assignments**
   - Dashboard shows current and upcoming cleaning assignments
   - Filter by status: Pending, In Progress, Completed
   - View trainset details and special instructions

3. **Take Photos After Cleaning**
   - Click "Start Assignment" on a pending task
   - Use "Take Photo" button to access device camera
   - Capture photos of cleaned areas (Interior, Exterior, Seats, etc.)
   - Photos are automatically uploaded and sent to AI for evaluation

4. **AI Evaluation Process**
   - Each photo is processed by Gemini AI
   - AI provides quality score (0-100)
   - Quality rating: Excellent, Good, Satisfactory, Needs Improvement
   - Detailed feedback and recommendations
   - Automatic approval for scores ≥ 75%

5. **Complete Assignment**
   - Mark assignment as completed
   - Add completion notes
   - System records actual completion time

### For Management:

1. **View Cleaning Data**
   - Go to trainset details in management dashboard
   - New "Cleaning Information" section shows:
     - Quality summary with average AI scores
     - Recent cleaning assignments
     - AI photo evaluations with ratings
     - Team assignment history

2. **Monitor Performance**
   - Track cleaning quality across teams
   - View AI evaluation results
   - Monitor assignment completion rates
   - Access team contact information

## API Endpoints

### Cleaning Authentication
- `POST /cleaning/login` - Cleaning team login
- `GET /cleaning/me` - Get current cleaner info

### Team Management
- `GET /cleaning/teams` - List all teams
- `GET /cleaning/teams/{team_id}` - Get team details
- `GET /cleaning/teams/{team_id}/members` - Get team members

### Assignments
- `GET /cleaning/assignments` - Get assignments for current user
- `GET /cleaning/assignments/{assignment_id}` - Get assignment details
- `PUT /cleaning/assignments/{assignment_id}/start` - Start assignment
- `PUT /cleaning/assignments/{assignment_id}/complete` - Complete assignment

### Photo Upload & AI Evaluation
- `POST /cleaning/assignments/{assignment_id}/photos` - Upload photo for AI evaluation
- `GET /cleaning/photos/{photo_id}` - Get photo evaluation details

### Management Integration
- `GET /trainsets/{trainset_id}/cleaning-info` - Get cleaning data for trainset

## File Structure

### Backend Files
```
backend/
├── app/
│   ├── models/
│   │   └── models.py              # Database models for cleaning
│   ├── routers/
│   │   ├── cleaning.py            # Cleaning API endpoints
│   │   └── trainsets.py           # Updated with cleaning integration
│   └── services/
│       └── gemini_service.py      # AI evaluation service
├── setup_cleaning_data.py         # Database setup script
└── requirements.txt               # Updated dependencies
```

### Frontend Files
```
frontend/
├── src/
│   ├── pages/
│   │   ├── CleaningLogin.js       # Cleaning team login page
│   │   ├── CleaningDashboard.js   # Main cleaning dashboard
│   │   └── TrainsetDetail.js      # Updated with cleaning info
│   └── App.js                     # Updated with cleaning routes
```

## Technical Features

### Camera Integration
- Real-time camera access using `getUserMedia` API
- Canvas-based photo capture
- File upload with multipart/form-data
- Automatic compression and optimization

### AI Evaluation
- Google Gemini API integration
- Detailed prompt engineering for cleaning assessment
- Structured evaluation criteria
- Confidence scoring and recommendations

### Database Relationships
- Proper foreign key relationships
- Optimized queries for performance
- JSON fields for flexible data storage
- Indexed fields for fast lookups

## Security Features

- Separate authentication system for cleaning teams
- JWT token-based security
- Role-based access control
- Secure file upload handling
- API key protection for Gemini integration

## Testing the System

### 1. Basic Flow Test
1. Login as cleaner1
2. View available assignments
3. Start an assignment
4. Take a photo using camera
5. Check AI evaluation results
6. Complete assignment
7. View results in management dashboard

### 2. AI Evaluation Test
1. Upload different types of photos
2. Test various cleaning scenarios
3. Verify AI scoring consistency
4. Check feedback quality

### 3. Management Integration Test
1. Login to management dashboard
2. Go to trainset details
3. Verify cleaning information displays
4. Check team assignment data
5. Review AI evaluation results

## Troubleshooting

### Common Issues

1. **Camera Access Denied**
   - Ensure HTTPS or localhost
   - Check browser permissions
   - Use supported browser (Chrome, Firefox, Safari)

2. **AI Evaluation Fails**
   - Check API key configuration
   - Verify internet connection
   - Check image format support

3. **Photo Upload Issues**
   - Check file size limits
   - Verify backend upload directory exists
   - Check network connectivity

### Performance Tips

1. **Image Optimization**
   - Compress photos before upload
   - Use appropriate image formats
   - Limit photo resolution

2. **Database Performance**
   - Regular database maintenance
   - Index optimization
   - Query caching

## Support

For technical support or questions:
- Check server logs for error details
- Use browser developer tools for frontend issues
- Test API endpoints directly for backend problems
- Verify database connectivity and data integrity

## Next Steps

1. **Production Deployment**
   - Configure environment variables
   - Set up SSL certificates
   - Implement backup strategies
   - Monitor system performance

2. **Enhanced Features**
   - Photo comparison before/after
   - Advanced AI analysis
   - Real-time notifications
   - Performance analytics dashboard

---

**System Status**: Ready for testing and demonstration
**Last Updated**: {{current_date}}
**Version**: 1.0.0