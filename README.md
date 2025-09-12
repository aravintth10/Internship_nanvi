# Person Profile Tracker v3.0

A comprehensive Django-based web application for searching and matching candidate profiles across multiple social media platforms and professional networks.

## 🚀 Features

### Core Functionality
- **Multi-Platform Search**: Search candidates across GitHub, Twitter/X, YouTube, LinkedIn, Facebook, and Instagram
- **File Upload & Analysis**: Upload candidate photos for face recognition and matching
- **Confidence Scoring**: Advanced scoring system based on name matching, face recognition, metadata, and activity
- **Real-time Results**: Instant search results with detailed candidate information

### API Integrations
- **GitHub API**: Search users by name and location
- **Twitter/X API**: Find profiles by username
- **YouTube Data API**: Search for channels and content creators
- **Google Scraping**: Public profile discovery for LinkedIn, Facebook, and Instagram

### Advanced Features
- **Face Recognition**: Compare uploaded photos with profile images
- **Location Matching**: Enhanced scoring for location-based matches
- **Activity Analysis**: Score based on social media activity and engagement
- **Secure API Management**: Environment-based API key management

## 🛠️ Technology Stack

- **Backend**: Django 5.0.3
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **APIs**: GitHub, Twitter/X, YouTube Data API
- **Image Processing**: OpenCV, face_recognition
- **Web Scraping**: BeautifulSoup4, requests
- **Database**: SQLite (development), PostgreSQL ready

## 📋 Requirements

### Python Dependencies
```
Django>=5.0.3
requests>=2.31.0
beautifulsoup4>=4.12.0
opencv-python>=4.8.0
face-recognition>=1.3.0
python-dotenv>=1.0.0
Pillow>=10.0.0
```

### API Keys Required
- GitHub Personal Access Token
- Twitter/X Bearer Token
- YouTube Data API Key

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PersonProfileTracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GITHUB_API_KEY=your_github_token_here
   TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
   YOUTUBE_API_KEY=your_youtube_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## 📊 Scoring System

The application uses a sophisticated scoring algorithm with the following weights:

- **Name Matching (20%)**: Exact and partial name matches
- **Face Recognition (40%)**: Image similarity using face recognition
- **Metadata Analysis (30%)**: Location, bio, and profile information
- **Activity Score (10%)**: Social media activity and engagement

### Confidence Score Calculation
```
Total Score = (Name Score × 0.2) + (Image Score × 0.4) + (Metadata Score × 0.3) + (Activity Score × 0.1) + Boost
```

## 🔧 Configuration

### API Configuration
All API keys are managed through environment variables for security:

- `GITHUB_API_KEY`: GitHub Personal Access Token
- `TWITTER_BEARER_TOKEN`: Twitter/X API Bearer Token  
- `YOUTUBE_API_KEY`: YouTube Data API v3 Key

### Debug Mode
Set `DEBUG=True` in your `.env` file to enable detailed logging of API calls and scoring calculations.

## 📁 Project Structure

```
PersonProfileTracker/
├── manage.py
├── person_profile_tracker/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── profiles/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── admin.py
│   └── templates/
│       └── profiles/
│           └── candidate_search.html
├── static/
├── media/
├── uploads/
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## 🔒 Security Features

- Environment-based API key management
- Secure file upload handling
- Input validation and sanitization
- CSRF protection enabled
- XSS protection through Django's built-in security

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📈 Performance

- Optimized API calls with caching
- Efficient face recognition processing
- Responsive Bootstrap UI
- Fast search results with real-time scoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the debug logs for API errors
- Ensure all API keys are properly configured

## 🎯 Roadmap

### Version 1.1 (Planned)
- Enhanced LinkedIn scraping
- Facebook/Instagram API integration
- Advanced filtering options
- Export functionality

### Version 1.2 (Planned)
- Machine learning-based matching
- Batch processing
- API rate limit management
- Mobile-responsive improvements

---

**Version 1.0** - Released July 9, 2025
- Complete multi-platform search functionality
- Face recognition and confidence scoring
- Secure API integration
- Production-ready Django application 
