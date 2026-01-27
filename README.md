# **🌱 GreenHabit - Eco Score Tracker**

## **📌 Project Overview**
GreenHabit is a web application that helps users track and improve their environmental impact through daily habit monitoring and scoring. The app calculates personalized eco-scores based on lifestyle choices and provides actionable recommendations for sustainable living.

![GreenHabit Banner](https://img.shields.io/badge/GreenHabit-Eco%20Tracker-2ecc71?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)

## **✨ Key Features**

### **🏠 Dual Mode System**
- **Home/Personal Mode**: Track individual environmental footprint
- **Business/Organization Mode**: Measure corporate sustainability
- Each mode offers **Quick** (4 questions) and **Detailed** (6-8 questions) assessments

### **📊 Smart Scoring Algorithm**
```python
# Sample Scoring Logic
plastic_scores = {'No': 25, 'Low': 15, 'High': 5, 'Yes': 5}
transport_scores = {'Walking': 25, 'Bicycle': 25, 'Public transport': 20, 'Car': 5}
food_scores = {'Vegetarian': 25, 'Mixed': 15, 'Non-vegetarian': 5}
energy_scores = {'Low': 25, 'Medium': 15, 'High': 5}
```

### **🎯 Progress Tracking**
- **Daily Streaks**: Encourages consistent eco-friendly habits
- **Score History**: Visual timeline of environmental progress
- **Monthly Goals**: 30-day challenge system
- **Personalized Tips**: AI-generated improvement suggestions

### **📱 Categories Covered**

#### **Home Mode Categories:**
- 🏭 Plastic Usage
- 🚗 Transportation Methods
- 🥗 Food Choices
- ⚡ Energy Consumption
- 💧 Water Usage (Detailed mode)
- 🗑️ Waste Management (Detailed mode)

#### **Business Mode Categories:**
- ⚡ Energy Efficiency
- 🚚 Transportation Logistics
- ♻️ Waste Management
- 📦 Supply Chain Sustainability
- 🌍 Carbon Footprint
- 👥 Employee Engagement

## **🚀 Quick Start**

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/greenhabit.git
cd greenhabit
```

2. **Install dependencies:**
```bash
pip install flask sqlite3
```

3. **Run the application:**
```bash
python app.py
```

4. **Open in browser:**
```
http://localhost:5000
```

## **🛠️ Technology Stack**

### **Frontend**
- **HTML5/CSS3**: Modern semantic markup with CSS Grid/Flexbox
- **JavaScript**: Vanilla ES6+ for interactive features
- **Font Awesome**: Icons for intuitive UI
- **Responsive Design**: Mobile-first approach

### **Backend**
- **Flask**: Lightweight Python web framework
- **SQLite**: File-based database for easy deployment
- **JSON Storage**: Flexible data handling for diverse question sets
- **Session Management**: Secure user authentication

### **Scoring Engine**
- **Python Logic**: Custom scoring algorithms for each mode
- **Dynamic Weighting**: Different scoring weights based on assessment type
- **Real-time Calculation**: Instant feedback on environmental impact

## **📊 Scoring Methodology**

### **Score Interpretation**
- **🟢 80-100**: **Excellent** - Outstanding environmental practices
- **🟡 60-79**: **Good** - Above average, room for improvement
- **🔴 0-59**: **Needs Improvement** - Significant environmental impact

### **Calculation Logic**
1. Each category contributes up to 25 points
2. Different scoring weights for Home vs Business modes
3. Detailed assessments provide more granular scoring
4. Real-time feedback with visual indicators

## **🎨 User Interface**

### **Dashboard Features**
- **Visual Score Display**: Circular progress indicator with color coding
- **Category Breakdown**: Individual scores for each habit category
- **Progress Timeline**: Historical data visualization
- **Personalized Tips**: Context-aware improvement suggestions

### **Design Principles**
- **Clean & Intuitive**: Minimalist design focusing on usability
- **Color Psychology**: Green-based palette for environmental theme
- **Accessibility**: WCAG 2.1 compliant design
- **Dark/Light Mode**: Automatic theme switching based on system preferences

## **📈 Project Structure**

```
greenhabit/
│
├── app.py                    # Main Flask application
├── greenhabit.db             # SQLite database
│
├── templates/                # HTML templates
│   ├── base.html            # Base layout template
│   ├── home.html            # Landing page
│   ├── generate.html        # Score calculation interface
│   ├── auth_profile.html    # User profile dashboard
│   ├── auth_login.html      # Login page
│   ├── auth_register.html   # Registration page
│   └── methodology.html     # Project explanation
│
├── static/                  # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
└── README.md               # This documentation
```

## **🔧 Configuration**

### **Environment Variables**
Create a `.env` file:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///greenhabit.db
```

### **Database Schema**
```sql
-- Core Tables
users (id, username, email, password, eco_streak, total_score, total_days)
user_habits (id, user_id, date, mode, assessment_type, habits_json, eco_score)
```

## **🎯 Use Cases**

### **For Individuals**
- 🏠 **Homeowners**: Track household environmental impact
- 🎓 **Students**: Learn about sustainability practices
- 🏢 **Office Workers**: Monitor daily commute and office habits
- 🛒 **Consumers**: Make informed eco-friendly purchasing decisions

### **For Businesses**
- 📊 **Sustainability Teams**: Track corporate environmental metrics
- 📈 **CSR Departments**: Generate sustainability reports
- 🏭 **Manufacturing**: Monitor production environmental impact
- 🏪 **Retail**: Assess supply chain sustainability

## **🌟 Benefits**

### **Environmental Impact**
- 📉 **Reduced Carbon Footprint**: Data-driven habit changes
- 🗑️ **Less Waste**: Improved recycling and consumption habits
- 💡 **Energy Conservation**: Optimized energy usage patterns
- 🚗 **Sustainable Transport**: Encouragement of eco-friendly commuting

### **Personal Benefits**
- 💰 **Cost Savings**: Reduced utility bills through conservation
- 🏆 **Achievement Tracking**: Gamified progress system
- 📚 **Education**: Learn about environmental impact factors
- 🤝 **Community**: Join like-minded eco-conscious individuals

## **🔍 How It Works**

### **1. Assessment Process**
```
Select Mode → Answer Questions → Get Score → View Breakdown → Receive Tips
```

### **2. Scoring Process**
```python
def calculate_eco_score(habits, mode):
    total_score = 0
    for category, value in habits.items():
        total_score += scoring_matrix[mode][category][value]
    return min(total_score, 100)
```

### **3. Tip Generation**
```python
def generate_tip(score, habits):
    lowest_category = identify_lowest_scoring_category(habits)
    return improvement_tips[lowest_category]
```

## **📱 Mobile Responsiveness**

| Device | Features |
|--------|----------|
| **Mobile** | Simplified interface, touch-friendly buttons |
| **Tablet** | Optimized layouts, enhanced readability |
| **Desktop** | Full feature set, advanced analytics |

## **🔒 Security & Privacy**

### **Data Protection**
- 🔐 **Password Hashing**: SHA-256 encryption
- 🛡️ **Session Security**: Flask session management
- 📜 **Input Validation**: Protection against XSS and SQL injection
- 🔒 **HTTPS Ready**: Secure data transmission

### **Privacy Features**
- 👤 **User Control**: Complete data ownership
- 🗑️ **Account Deletion**: One-click account removal
- 📊 **Data Anonymization**: Optional anonymous data collection
- 📜 **GDPR Compliance**: Privacy-focused design

### **Test Categories**
- ✅ Scoring algorithm accuracy
- ✅ Database operations
- ✅ User authentication
- ✅ Form validation
- ✅ API endpoints

## **🤝 Contributing**

### **Getting Started**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### **Development Guidelines**
- Follow PEP 8 for Python code
- Use semantic HTML5 markup
- Write comprehensive documentation
- Add tests for new features

### **Areas for Contribution**
- 🌍 Additional environmental categories
- 📊 Advanced analytics features
- 📱 Mobile app development
- 🔌 Third-party integrations
- 🌐 Internationalization

## **📄 License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 GreenHabit Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## **🙏 Acknowledgments**

### **Inspiration**
- United Nations Sustainable Development Goals
- Carbon footprint calculators worldwide
- Environmental education initiatives
- Sustainable lifestyle advocates

### **Technologies**
- Flask web framework
- SQLite database
- Font Awesome icons
- Various open-source libraries


---

**Disclaimer:** GreenHabit provides environmental impact estimates based on general data. For precise carbon calculations, consult with environmental professionals.
