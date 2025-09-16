# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Prepare Your Repository
- Ensure all code is committed to GitHub
- The `.streamlit/secrets.toml` file is ignored by git (already configured)

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `chat-bot - Copy`
5. Main file path: `app.py`
6. Click "Deploy!"

### 3. Add Your Gemini API Key
1. In your Streamlit Cloud dashboard, click on your app
2. Go to "Settings" → "Secrets"
3. Add the following secret:

```toml
GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

4. Click "Save"
5. Your app will automatically restart with the new secret

## ✅ What's Already Configured

- ✅ Code updated to use Streamlit secrets
- ✅ Fallback to environment variables for local development
- ✅ `.gitignore` updated to exclude secrets
- ✅ Local secrets file for development (`.streamlit/secrets.toml`)

## 🔧 Local Development

For local development, your API key is already configured in `.streamlit/secrets.toml`

Run locally:
```bash
streamlit run app.py
```

## 🌐 Production URL

After deployment, your app will be available at:
`https://[your-app-name].streamlit.app`

## 🔒 Security Notes

- Never commit API keys to git
- Use Streamlit Cloud secrets for production
- The local secrets file is ignored by git
- API keys are securely stored in Streamlit Cloud

## 📝 Next Steps After Deployment

1. Test all functionality on the live app
2. Share the URL with stakeholders
3. Monitor usage in Streamlit Cloud dashboard
4. Consider custom domain (available in Streamlit Cloud)