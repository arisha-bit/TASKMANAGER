# Enhanced Task Manager Pro 🚀

A beautiful, AI-powered task management application that extracts tasks from images (datasheets, schedules) using advanced OCR technology and integrates with Google Calendar, Google Tasks, and MongoDB.

## ✨ Features

### 🖼️ **Smart Image Processing**
- **Advanced OCR**: Enhanced image preprocessing with OpenCV for better text extraction
- **Table Recognition**: Optimized for datasheets and structured documents
- **Multiple Date Formats**: Supports DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD, and more
- **Drag & Drop**: Intuitive file upload with preview

### 📊 **Task Management**
- **Priority Levels**: High, Medium, Low priority classification
- **Status Tracking**: Pending, In Progress, Completed, Cancelled
- **Rich Metadata**: Tags, descriptions, timestamps
- **Search & Filter**: Advanced filtering by status, priority, and text search

### 🔄 **Integration**
- **Google Calendar**: Automatic event creation
- **Google Tasks**: Sync with Google Tasks
- **MongoDB**: Robust data storage with indexing
- **REST API**: Full API endpoints for external integration

### 🎨 **Beautiful UI**
- **Lavender Theme**: Modern, soothing color scheme
- **Responsive Design**: Works on all devices
- **Smooth Animations**: CSS animations and transitions
- **Interactive Elements**: Hover effects and micro-interactions

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas)
- Google Cloud Project with Calendar and Tasks APIs enabled
- Tesseract OCR engine

### 1. Clone the Repository
```bash
git clone <repository-url>
cd taskmanager
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR
```bash
# Windows (using chocolatey)
choco install tesseract

# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

### 5. Configure Environment
Create a `.env` file in the root directory:
```env
MONGO_URI=your_mongodb_connection_string
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
```

### 6. Set up Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API and Google Tasks API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file
6. Place it in the project root as `credentials.json`

## 🚀 Usage

### Start the Application
```bash
python -m app.main
```

The application will be available at `http://localhost:8000`

### Basic Workflow
1. **Upload Image**: Drag & drop or browse for an image file
2. **Extract Tasks**: AI processes the image and extracts tasks with dates
3. **Review & Edit**: Modify task details, priorities, and status
4. **Sync**: Tasks automatically sync with Google Calendar and Tasks
5. **Manage**: Use the dashboard to track progress and manage tasks

## 📁 Project Structure

```
taskmanager/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # MongoDB operations
│   ├── models.py            # Pydantic models
│   ├── ocr.py              # Image processing & OCR
│   ├── google_auth.py      # Google OAuth
│   ├── google_calendar.py  # Calendar integration
│   └── google_tasks.py     # Tasks integration
├── static/
│   ├── css/
│   │   └── style.css       # Beautiful lavender theme
│   └── script.js           # Enhanced JavaScript
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── upload.html         # Upload results
│   ├── tasks.html          # Task management
│   └── dashboard.html      # Dashboard
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### MongoDB Connection
Update `app/database.py` with your MongoDB connection string:
```python
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
```

### Google API Credentials
1. Place your `credentials.json` in the project root
2. Update OAuth scopes in `app/google_auth.py` if needed

### OCR Configuration
Modify `app/ocr.py` to adjust:
- Image preprocessing parameters
- Date format recognition patterns
- Text extraction settings

## 📱 API Endpoints

### Web Routes
- `GET /` - Home page with upload functionality
- `GET /dashboard` - Task statistics and overview
- `GET /tasks` - Task management page
- `POST /upload` - Image upload and task extraction

### API Endpoints
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{task_id}` - Get specific task
- `GET /api/stats` - Get task statistics

### Task Operations
- `POST /tasks/complete` - Mark task as complete
- `POST /tasks/delete` - Delete task
- `POST /tasks/update` - Update task details

## 🎨 Customization

### Colors & Theme
The application uses a beautiful lavender theme. Customize colors in `static/css/style.css`:
```css
:root {
    --primary-color: #967BB6;
    --secondary-color: #B19CD9;
    --accent-color: #E6E6FA;
    --text-color: #4A4A6A;
    --background-color: #F8F8FF;
}
```

### Adding New Features
1. **New Models**: Add to `app/models.py`
2. **Database Operations**: Extend `app/database.py`
3. **API Endpoints**: Add routes in `app/main.py`
4. **UI Components**: Create new templates and styles

## 🚀 Deployment

### Production Setup
1. **Environment Variables**: Set production environment variables
2. **Database**: Use production MongoDB instance
3. **Google OAuth**: Update redirect URIs for production domain
4. **Static Files**: Serve static files through a web server
5. **Process Manager**: Use PM2 or similar for process management

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

#### OCR Not Working
- Ensure Tesseract is installed and in PATH
- Check image quality and format
- Verify Tesseract language packs

#### Google Integration Fails
- Check OAuth credentials
- Verify API scopes are enabled
- Check redirect URI configuration

#### MongoDB Connection Issues
- Verify connection string
- Check network access
- Ensure database exists

### Debug Mode
Enable debug logging in `app/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** for the modern web framework
- **OpenCV** for image processing capabilities
- **Tesseract** for OCR functionality
- **Google APIs** for calendar and tasks integration
- **MongoDB** for robust data storage

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**Made with ❤️ and ☕ for better task management**
