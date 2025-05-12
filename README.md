# Advanced Customer Feedback Management System

A comprehensive feedback management system built with Python Flask that allows users to submit, track, and analyze customer feedback.

## Features

- User authentication and authorization
- Feedback submission with ratings and categories
- Sentiment analysis of feedback content
- Admin dashboard for feedback management
- Real-time analytics and reporting
- Responsive and modern UI
- Feedback status tracking
- Category-based organization
- Interactive charts and statistics

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd feedback-management-system
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following content:
```
SECRET_KEY=your-secret-key-here
```

5. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Access the application in your web browser:
```
http://localhost:5000
```

3. Register a new account or log in with existing credentials

4. Submit feedback and track its status

5. For admin access, set the `is_admin` flag to `True` in the database for your user account

## Admin Features

- View all feedback submissions
- Respond to feedback
- Update feedback status
- View analytics and statistics
- Filter feedback by status
- Track resolution rates

## User Features

- Submit feedback with ratings
- Choose feedback categories
- Track feedback status
- View feedback history
- Receive responses from administrators

## Technologies Used

- Flask (Web Framework)
- SQLAlchemy (ORM)
- TextBlob (Sentiment Analysis)
- Chart.js (Data Visualization)
- Bootstrap 5 (UI Framework)
- SQLite (Database)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 