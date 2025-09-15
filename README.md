# 🚛 Stephex Horse Trucks - AI Chatbot Demo

A professional, multi-language chatbot demo for Stephex Horse Trucks to improve customer conversion rates and provide instant assistance to website visitors.

## ✨ Features

- **Multi-language Support**: English, Spanish, French, German, Portuguese
- **Intelligent Conversation**: Context-aware responses and intent recognition
- **Modern UI**: Professional design with smooth animations
- **Lead Qualification**: Budget detection and preference tracking
- **Quick Actions**: Fast access to common inquiries
- **Responsive Design**: Works on desktop and mobile
- **Easy Deployment**: One-click deployment to Streamlit Cloud

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone or download the project**
```bash
git clone <repository-url>
cd chat-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run app.py
```

4. **Open your browser**
Navigate to `http://localhost:8501`

## 📁 Project Structure

```
chat-bot/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── assets/
│   └── css/
│       └── style.css          # Custom CSS styling
└── src/
    ├── components/
    │   ├── chatbot_engine.py   # Main conversation logic
    │   └── ui_components.py    # UI components and styling
    ├── config/
    │   └── settings.py         # App configuration
    ├── data/
    │   └── sample_data.py      # Sample truck and company data
    └── utils/
        ├── chat_utils.py       # Chat utilities and session management
        └── language_manager.py # Multi-language support
```

## 🎯 Chatbot Capabilities

### Core Features
- **Lead Qualification**: Automatically detects budget and preferences
- **Product Recommendations**: Suggests trucks based on user needs
- **Financing Information**: Provides loan options and calculations
- **Contact Management**: Handles appointment scheduling and contact requests
- **Multi-language**: Automatic translation and language detection

### Conversation Flow
1. **Greeting**: Welcomes users and offers assistance
2. **Needs Assessment**: Asks about budget, truck type, and requirements
3. **Recommendations**: Shows relevant trucks and options
4. **Lead Capture**: Collects contact information when appropriate
5. **Follow-up**: Schedules visits or provides next steps

## 🌐 Multi-language Support

The chatbot supports 5 languages:
- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇵🇹 Portuguese (pt)

Language can be:
- **Manually selected** by users (current implementation)
- **Auto-detected** from user input
- **IP-based detection** (for production deployment)

## 🔧 Customization

### Adding New Languages
1. Update `SUPPORTED_LANGUAGES` in `src/config/settings.py`
2. Add translations in `src/utils/language_manager.py`
3. Test the new language functionality

### Modifying Truck Data
1. Edit `src/data/sample_data.py`
2. Update `SAMPLE_TRUCKS`, `FINANCING_OPTIONS`, and `COMPANY_INFO`
3. Restart the application

### Styling Changes
1. Modify `assets/css/style.css`
2. Update colors in `src/config/settings.py`
3. Refresh the browser

## 🚀 Deployment Options

### Streamlit Cloud (Recommended)
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with one click
4. **Free hosting** with custom domain options

### Alternative Deployments
- **Heroku**: Easy deployment with buildpacks
- **Railway**: Modern deployment platform
- **Docker**: Containerized deployment
- **AWS/GCP**: Cloud platform deployment

## 🔄 Migration to Website Integration

This chatbot is designed for easy integration:

### Phase 1: Standalone Demo
- Current Streamlit application
- Perfect for testing and refinement

### Phase 2: Website Embed
```html
<iframe src="https://your-chatbot.streamlit.app" 
        width="400" height="600" 
        style="border:none; border-radius:10px;">
</iframe>
```

### Phase 3: API Integration
- Extract backend logic to FastAPI
- Create custom frontend
- Full website integration

## 📊 Analytics & Tracking

The chatbot tracks:
- **Conversation metrics**: Message counts and session length
- **User preferences**: Budget and truck type preferences
- **Lead quality**: Contact information collection
- **Popular inquiries**: Most asked questions

## 🛠️ Development

### Adding New Features
1. **New Intents**: Add to `extract_intent()` in `chat_utils.py`
2. **Response Handlers**: Create new methods in `chatbot_engine.py`
3. **UI Components**: Add to `ui_components.py`
4. **Configuration**: Update `settings.py`

### Testing
- Test all language combinations
- Verify conversation flows
- Check mobile responsiveness
- Validate lead capture functionality

## 📞 Support

For questions or customization requests:
- Review the code documentation
- Check the configuration files
- Test with sample data first
- Ensure all dependencies are installed

## 🎉 Next Steps

1. **Add Real Data**: Replace sample data with actual truck inventory
2. **Enhanced AI**: Integrate with OpenAI or other AI services
3. **CRM Integration**: Connect with customer management systems
4. **Analytics**: Add detailed conversation analytics
5. **A/B Testing**: Test different conversation flows

---

**Built with ❤️ for Stephex Horse Trucks**
*Improving customer experience through intelligent conversation*