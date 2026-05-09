# Nexus Analytics – Automated AI Report Generator

An AI-powered analytics platform that automatically processes datasets, generates visualizations, extracts insights using LLMs, and creates downloadable PDF reports.

## Features

- Upload CSV, XLSX, and XLS files
- Supports datasets up to 50MB
- AI-generated insights using Gemini API
- Automatic chart and graph generation
- PDF report export
- Interactive analytics dashboard
- Fullstack architecture using Next.js and FastAPI

## Tech Stack

### Frontend
- Next.js
- React
- Tailwind CSS
- Axios
- Lucide Icons

### Backend
- FastAPI
- Python
- Pandas
- Matplotlib
- Google Gemini API
- ReportLab

## Project Structure

```bash
frontend/
backend/
```

## Setup Instructions

### Backend

```bash
cd backend

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

## Environment Variables

Create `.env` inside backend:

```env
GEMINI_API_KEY=your_api_key
```

## Future Improvements

## Future Improvements

- User authentication and secure login system  
- Database integration for persistent data storage  
- Advanced analytics and intelligent reporting  
- Support for additional file formats  
- Export reports in multiple formats  
- Dark and light theme support  
- Machine learning-based predictive analytics  
- Chat-based AI data assistant  
- Cloud deployment and scalability improvements  

## Author

Karwan Kamboj
