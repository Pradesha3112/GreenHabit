from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key
DATABASE = 'greenhabit.db'

# Database initialization
def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            eco_streak INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            total_days INTEGER DEFAULT 0
        )
    ''')
    
    # User habits table - UPDATED SCHEMA
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            mode TEXT DEFAULT 'home',  -- 'home' or 'business'
            assessment_type TEXT DEFAULT 'quick',  -- 'quick' or 'detailed'
            habits_json TEXT NOT NULL,  -- Store all habits as JSON
            eco_score INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, date, mode, assessment_type)
        )
    ''')
    
    # Create index for faster queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON user_habits(user_id, date)')
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Calculate eco score functions for different modes
def calculate_home_score(data, assessment_type='quick'):
    """Calculate eco-score for home/personal mode"""
    score = 0
    
    # Calculate plastic score
    plastic = data.get('plastic', '')
    if assessment_type == 'quick':
        plastic_scores = {'No': 25, 'Low': 15, 'High': 5, 'Yes': 5}
    else:
        plastic_scores = {'No': 25, 'Low': 18, 'Medium': 12, 'High': 6, 'Yes': 6, 'Recycled': 15}
    score += plastic_scores.get(plastic, 0)
    
    # Calculate transport score
    transport = data.get('transport', '')
    if assessment_type == 'quick':
        transport_scores = {
            'Walking': 25, 'Bicycle': 25, 'Public transport': 20,
            'Car': 5
        }
    else:
        transport_scores = {
            'Walking': 25, 'Bicycle': 25, 'Public transport': 20,
            'Car': 8, 'Electric vehicle': 18, 'Hybrid car': 15, 
            'Gas car': 5, 'Multiple': 12
        }
    score += transport_scores.get(transport, 0)
    
    # Calculate food score
    food = data.get('food', '')
    if assessment_type == 'quick':
        food_scores = {'Vegetarian': 25, 'Mixed': 15, 'Non-vegetarian': 5}
    else:
        food_scores = {
            'Vegan': 25, 'Vegetarian': 20, 'Mostly veg': 16,
            'Mixed': 12, 'Mostly meat': 8, 'Local produce': 22
        }
    score += food_scores.get(food, 0)
    
    # Calculate energy score
    energy = data.get('energy', '')
    if assessment_type == 'quick':
        energy_scores = {'Low': 25, 'Medium': 15, 'High': 5}
    else:
        energy_scores = {
            'Very Low': 25, 'Low': 20, 'Medium': 15,
            'High': 8, 'Renewable': 22
        }
    score += energy_scores.get(energy, 0)
    
    # Additional categories for detailed home assessment
    if assessment_type == 'detailed':
        water = data.get('water', '')
        water_scores = {'Conservative': 10, 'Low': 8, 'Medium': 6, 'High': 4}
        score += water_scores.get(water, 0)
        
        waste = data.get('waste', '')
        waste_scores = {'Compost': 10, 'Recycle All': 8, 'Most Recycled': 6, 'Some Recycled': 4, 'Landfill': 2}
        score += waste_scores.get(waste, 0)
    
    return min(score, 100)

def calculate_business_score(data, assessment_type='quick'):
    """Calculate eco-score for business/organization mode"""
    score = 0
    
    # Calculate energy score
    energy = data.get('energy', '')
    if assessment_type == 'quick':
        energy_scores = {
            'Renewable': 25, 'Efficient': 20, 'Average': 15, 'High': 5
        }
    else:
        energy_scores = {
            'Renewable 100': 25, 'Renewable 50': 20, 'Efficient': 18,
            'LED Lighting': 16, 'Standard': 10, 'High': 5
        }
    score += energy_scores.get(energy, 0)
    
    # Calculate transport score
    transport = data.get('transport', '')
    if assessment_type == 'quick':
        transport_scores = {
            'Remote': 25, 'Public': 20, 'Mixed': 15, 'Vehicle': 10
        }
    else:
        transport_scores = {
            'Electric Fleet': 25, 'Hybrid Fleet': 20, 'Route Opt': 18,
            'Remote Work': 22, 'Standard': 10
        }
    score += transport_scores.get(transport, 0)
    
    # Calculate waste score
    waste = data.get('waste', '')
    if assessment_type == 'quick':
        waste_scores = {
            'Zero Waste': 25, 'Recycle Most': 20, 'Some Recycle': 15, 'Basic': 10
        }
    else:
        waste_scores = {
            'Zero Waste': 25, 'Composting': 22, 'Recycle All': 20,
            'Recycle Some': 15, 'Basic': 10
        }
    score += waste_scores.get(waste, 0)
    
    # Calculate supply chain score
    supply = data.get('supply', '')
    if assessment_type == 'quick':
        supply_scores = {
            'Sustainable': 25, 'Local': 20, 'Mixed': 15, 'Standard': 10
        }
    else:
        supply_scores = {
            'Certified': 25, 'Local': 22, 'Audited': 18,
            'Some Local': 15, 'Standard': 10
        }
    score += supply_scores.get(supply, 0)
    
    # Additional categories for detailed business assessment
    if assessment_type == 'detailed':
        carbon = data.get('carbon', '')
        carbon_scores = {
            'Carbon Neutral': 10, 'Offsetting': 8, 'Measuring': 6,
            'Planning': 4, 'Basic': 2
        }
        score += carbon_scores.get(carbon, 0)
        
        water = data.get('water', '')
        water_scores = {
            'Rainwater': 10, 'Greywater': 8, 'Efficient': 6,
            'Monitoring': 4, 'Standard': 2
        }
        score += water_scores.get(water, 0)
        
        products = data.get('products', '')
        product_scores = {
            'Circular': 10, 'Biodegradable': 8, 'Recycled': 6,
            'Some Green': 4, 'Standard': 2
        }
        score += product_scores.get(products, 0)
        
        employee = data.get('employee', '')
        employee_scores = {
            'Green Team': 10, 'Training': 8, 'Programs': 6,
            'Basic': 4, 'None': 2
        }
        score += employee_scores.get(employee, 0)
    
    return min(score, 100)

def get_home_tip(score, data):
    """Generate tips for home mode"""
    if score >= 80:
        return "Excellent work! Your daily habits are highly eco-friendly. Keep inspiring others!"
    elif score >= 60:
        return "Good job! You're making conscious choices. Try to reduce plastic usage even further."
    else:
        # Find areas for improvement
        suggestions = []
        
        plastic = data.get('plastic', '')
        if plastic in ['High', 'Yes']:
            suggestions.append("carry reusable bags and containers")
        
        transport = data.get('transport', '')
        if transport == 'Car':
            suggestions.append("try walking or cycling for short trips")
        
        food = data.get('food', '')
        if food == 'Non-vegetarian':
            suggestions.append("try more plant-based meals")
        
        energy = data.get('energy', '')
        if energy == 'High':
            suggestions.append("switch off unused electronics")
        
        if suggestions:
            return f"Consider these improvements: {', '.join(suggestions)}"
        else:
            return "Every small change helps! Start by being mindful of your daily habits."

def get_business_tip(score, data):
    """Generate tips for business mode"""
    if score >= 80:
        return "Outstanding! Your business is a sustainability leader. Consider pursuing green certifications."
    elif score >= 60:
        return "Solid sustainability practices! Look into energy audits and carbon offset programs."
    else:
        # Find areas for improvement
        suggestions = []
        
        energy = data.get('energy', '')
        if energy in ['Average', 'High', 'Standard']:
            suggestions.append("switch to renewable energy sources")
        
        waste = data.get('waste', '')
        if waste in ['Some Recycle', 'Basic']:
            suggestions.append("implement comprehensive recycling programs")
        
        supply = data.get('supply', '')
        if supply in ['Mixed', 'Standard']:
            suggestions.append("work with local and sustainable suppliers")
        
        transport = data.get('transport', '')
        if transport in ['Vehicle', 'Standard']:
            suggestions.append("promote remote work and eco-friendly commuting")
        
        if suggestions:
            return f"Business improvements: {', '.join(suggestions)}. Small changes can reduce costs and attract eco-conscious customers."
        else:
            return "Start your sustainability journey with an energy audit and waste assessment."

def get_score_color(score):
    if score >= 80:
        return '#2ecc71'
    elif score >= 60:
        return '#f39c12'
    else:
        return '#e74c3c'

def get_score_label(score):
    if score >= 80:
        return 'Excellent'
    elif score >= 60:
        return 'Good'
    else:
        return 'Needs Improvement'

# Calculate streak function
def calculate_streak(user_id):
    """Calculate current streak for a user"""
    conn = get_db()
    
    # Get DISTINCT dates when user logged scores
    dates = conn.execute(
        '''SELECT DISTINCT date FROM user_habits 
           WHERE user_id = ? 
           ORDER BY date DESC''',
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    if not dates:
        return 0
    
    today = datetime.now().date()
    streak = 0
    
    # Convert database dates to datetime objects
    date_list = []
    for record in dates:
        try:
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()
            date_list.append(date_obj)
        except:
            continue
    
    if not date_list:
        return 0
    
    # Check if latest entry is today
    if date_list[0] == today:
        streak = 1
        # Check previous consecutive days
        for i in range(1, len(date_list)):
            expected_date = today - timedelta(days=i)
            if expected_date in date_list:
                streak += 1
            else:
                break
    else:
        # Check if yesterday was logged
        yesterday = today - timedelta(days=1)
        if date_list[0] == yesterday:
            streak = 1
            # Check previous consecutive days
            for i in range(2, len(date_list) + 1):
                expected_date = yesterday - timedelta(days=i-1)
                if expected_date in date_list:
                    streak += 1
                else:
                    break
    
    return streak

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/generate')
@login_required
def generate():
    return render_template('generate.html')

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            (username, username)
        ).fetchone()
        conn.close()
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            
            # Update last login
            conn = get_db()
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            conn.commit()
            conn.close()
            
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username/email or password', 'danger')
    
    return render_template('auth_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
                (username, email, hash_password(password), full_name)
            )
            conn.commit()
            
            # Get the new user
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            conn.close()
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            
            flash('Registration successful! Welcome to GreenHabit!', 'success')
            return redirect(url_for('home'))
            
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
            conn.close()
    
    return render_template('auth_register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# Profile Route - FIXED
@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (session['user_id'],)
    ).fetchone()
    
    # Calculate current streak
    current_streak = calculate_streak(session['user_id'])
    
    # Get user's recent habits
    habits = conn.execute(
        '''SELECT date, mode, assessment_type, habits_json, eco_score 
           FROM user_habits 
           WHERE user_id = ? 
           ORDER BY date DESC 
           LIMIT 10''',
        (session['user_id'],)
    ).fetchall()
    
    # Parse habits_json for display
    parsed_habits = []
    for habit in habits:
        parsed = dict(habit)
        try:
            parsed['habits'] = json.loads(habit['habits_json'])
        except:
            parsed['habits'] = {}
        parsed_habits.append(parsed)
    
    # Get user statistics - FIXED QUERY
    stats = conn.execute(
        '''SELECT 
               COUNT(DISTINCT date) as total_days,
               COUNT(*) as total_entries,
               AVG(eco_score) as avg_score,
               MAX(eco_score) as best_score,
               MIN(eco_score) as worst_score,
               COUNT(DISTINCT mode) as modes_used
           FROM user_habits 
           WHERE user_id = ?''',
        (session['user_id'],)
    ).fetchone()
    
    conn.close()
    
    # Handle None values in stats
    if stats:
        stats = dict(stats)
        # Convert None values to 0 for template rendering
        for key in stats:
            if stats[key] is None:
                stats[key] = 0
        # Round avg_score for display
        if stats['avg_score']:
            stats['avg_score'] = round(stats['avg_score'], 1)
    else:
        stats = {
            'total_days': 0,
            'total_entries': 0,
            'avg_score': 0,
            'best_score': 0,
            'worst_score': 0,
            'modes_used': 0
        }
    
    # Add streak to stats
    stats['current_streak'] = current_streak
    
    # Get current datetime for display
    current_datetime = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
    
    return render_template('auth_profile.html', 
                         user=user, 
                         habits=parsed_habits, 
                         stats=stats,
                         current_datetime=current_datetime)

# API Routes
@app.route('/api/calculate', methods=['POST'])
@login_required
def calculate():
    try:
        data = request.json
        
        # Extract mode and type
        mode = data.get('mode', 'home')
        assessment_type = data.get('type', 'quick')
        
        # Calculate score based on mode
        if mode == 'home':
            eco_score = calculate_home_score(data, assessment_type)
            tip = get_home_tip(eco_score, data)
        else:  # business mode
            eco_score = calculate_business_score(data, assessment_type)
            tip = get_business_tip(eco_score, data)
        
        # Prepare habits data (remove mode/type from habits)
        habits_data = {k: v for k, v in data.items() if k not in ['mode', 'type']}
        
        # Save to database
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db()
        
        # Store habits as JSON
        habits_json = json.dumps(habits_data)
        
        conn.execute(
            '''INSERT OR REPLACE INTO user_habits 
               (user_id, date, mode, assessment_type, habits_json, eco_score)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session['user_id'], today, mode, assessment_type, habits_json, eco_score)
        )
        
        # Update user stats - Only update total_days if it's a new unique day
        # First check if user already has an entry for today
        existing_today = conn.execute(
            'SELECT COUNT(*) as count FROM user_habits WHERE user_id = ? AND date = ?',
            (session['user_id'], today)
        ).fetchone()
        
        if existing_today['count'] == 1:  # This is the first entry today
            conn.execute(
                '''UPDATE users 
                   SET total_score = total_score + ?,
                       total_days = total_days + 1
                   WHERE id = ?''',
                (eco_score, session['user_id'])
            )
        else:
            # Just update the score
            conn.execute(
                '''UPDATE users 
                   SET total_score = total_score + ?
                   WHERE id = ?''',
                (eco_score, session['user_id'])
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'eco_score': eco_score,
            'score_color': get_score_color(eco_score),
            'score_label': get_score_label(eco_score),
            'tip': tip,
            'mode': mode,
            'assessment_type': assessment_type,
            'habits': habits_data
        })
        
    except Exception as e:
        app.logger.error(f"Error in calculate endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/user/stats')
@login_required
def user_stats():
    conn = get_db()
    
    # Calculate current streak
    current_streak = calculate_streak(session['user_id'])
    
    stats = conn.execute(
        '''SELECT 
               COUNT(DISTINCT date) as total_days,
               COUNT(*) as total_entries,
               AVG(eco_score) as avg_score,
               MAX(eco_score) as best_score,
               MIN(eco_score) as worst_score,
               COUNT(DISTINCT mode) as modes_used
           FROM user_habits 
           WHERE user_id = ?''',
        (session['user_id'],)
    ).fetchone()
    
    user = conn.execute(
        'SELECT total_score FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    
    conn.close()
    
    return jsonify({
        'total_days': stats['total_days'] or 0,  # Changed from total_entries
        'total_entries': stats['total_entries'] or 0,
        'avg_score': round(stats['avg_score'] or 0, 1),
        'best_score': stats['best_score'] or 0,
        'worst_score': stats['worst_score'] or 0,
        'modes_used': stats['modes_used'] or 0,
        'current_streak': current_streak,
        'total_score': user['total_score'] or 0
    })

@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.json
        
        # Verify current password
        conn = get_db()
        user = conn.execute(
            'SELECT password FROM users WHERE id = ?',
            (session['user_id'],)
        ).fetchone()
        
        if not user or user['password'] != hash_password(data.get('current_password', '')):
            return jsonify({'success': False, 'error': 'Incorrect current password'})
        
        # Update profile
        updates = []
        values = []
        
        if 'full_name' in data:
            updates.append('full_name = ?')
            values.append(data['full_name'])
        
        if 'email' in data:
            updates.append('email = ?')
            values.append(data['email'])
        
        if data.get('new_password'):
            updates.append('password = ?')
            values.append(hash_password(data['new_password']))
        
        if updates:
            values.append(session['user_id'])
            conn.execute(
                f'UPDATE users SET {", ".join(updates)} WHERE id = ?',
                values
            )
            conn.commit()
        
        conn.close()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/delete', methods=['DELETE'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        conn = get_db()
        
        # Delete user habits
        conn.execute('DELETE FROM user_habits WHERE user_id = ?', (session['user_id'],))
        
        # Delete user
        conn.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
        
        conn.commit()
        conn.close()
        
        # Clear session
        session.clear()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Database migration function
def migrate_database():
    """Migrate from old schema to new schema"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    try:
        # Check if old columns exist
        c.execute("PRAGMA table_info(user_habits)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'plastic' in columns and 'habits_json' not in columns:
            # Migrate old data
            print("Migrating database...")
            
            # Create new table
            c.execute('''
                CREATE TABLE user_habits_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    mode TEXT DEFAULT 'home',
                    assessment_type TEXT DEFAULT 'quick',
                    habits_json TEXT NOT NULL,
                    eco_score INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, date, mode, assessment_type)
                )
            ''')
            
            # Migrate existing data
            c.execute('SELECT * FROM user_habits')
            old_records = c.fetchall()
            
            for record in old_records:
                id, user_id, date, plastic, transport, food, energy, eco_score = record
                habits_data = {
                    'plastic': plastic,
                    'transport': transport,
                    'food': food,
                    'energy': energy
                }
                habits_json = json.dumps(habits_data)
                
                c.execute(
                    '''INSERT INTO user_habits_new 
                       (user_id, date, mode, assessment_type, habits_json, eco_score)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (user_id, date, 'home', 'quick', habits_json, eco_score)
                )
            
            # Drop old table and rename new one
            c.execute('DROP TABLE user_habits')
            c.execute('ALTER TABLE user_habits_new RENAME TO user_habits')
            
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.commit()
        conn.close()

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Migrate if needed
    migrate_database()
    
    app.run(debug=True)