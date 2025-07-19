#!/usr/bin/env python3
"""
Diabetes Tracker - Mobile Web App
Flask web applicatie die werkt op telefoon en computer
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import threading
import time

app = Flask(__name__)
app.secret_key = 'diabetes_tracker_secret_key_2024'

# Database setup
def init_mobile_database():
    """Initialiseer database voor mobile app"""
    conn = sqlite3.connect('mobile_diabetes.db')
    cursor = conn.cursor()
    
    # Bloedwaarden tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            blood_value REAL NOT NULL,
            medication TEXT,
            activity TEXT,
            weight REAL,
            notes TEXT,
            insulin_advice TEXT,
            insulin_taken BOOLEAN,
            insulin_missed BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Gebruikers tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            name TEXT,
            age INTEGER,
            diabetes_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Medicatie tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            dosage TEXT,
            time_slot TEXT,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Notificaties tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            message TEXT,
            scheduled_time TIMESTAMP,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Login vereist decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Hoofdpagina"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login pagina"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('mobile_diabetes.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Succesvol ingelogd!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Ongeldige gebruikersnaam of wachtwoord', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registratie pagina"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        age = request.form['age']
        diabetes_type = request.form['diabetes_type']
        
        conn = sqlite3.connect('mobile_diabetes.db')
        cursor = conn.cursor()
        
        # Controleer of gebruikersnaam al bestaat
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Gebruikersnaam bestaat al', 'error')
            conn.close()
            return render_template('register.html')
        
        # Maak nieuwe gebruiker
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, name, age, diabetes_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, email, name, age, diabetes_type))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        flash('Account succesvol aangemaakt!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Uitloggen"""
    session.clear()
    flash('Uitgelogd', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard pagina"""
    user_id = session['user_id']
    
    # Haal recente data op
    conn = sqlite3.connect('mobile_diabetes.db')
    cursor = conn.cursor()
    
    # Recente bloedwaarden
    cursor.execute('''
        SELECT date, time, blood_value, medication, activity, weight, notes
        FROM blood_readings 
        WHERE user_id = ? 
        ORDER BY date DESC, time DESC 
        LIMIT 10
    ''', (user_id,))
    recent_readings = cursor.fetchall()
    
    # Statistieken
    cursor.execute('''
        SELECT 
            COUNT(*) as total_readings,
            AVG(blood_value) as avg_blood,
            MIN(blood_value) as min_blood,
            MAX(blood_value) as max_blood,
            AVG(weight) as avg_weight
        FROM blood_readings 
        WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    
    # Vandaag statistieken
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT COUNT(*), AVG(blood_value)
        FROM blood_readings 
        WHERE user_id = ? AND date = ?
    ''', (user_id, today))
    today_stats = cursor.fetchone()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         recent_readings=recent_readings,
                         stats=stats,
                         today_stats=today_stats)

@app.route('/add_reading', methods=['GET', 'POST'])
@login_required
def add_reading():
    """Nieuwe meting toevoegen"""
    if request.method == 'POST':
        user_id = session['user_id']
        
        # Form data
        date = request.form['date']
        time = request.form['time']
        blood_value = float(request.form['blood_value'])
        medication = request.form.get('medication', '')
        activity = request.form.get('activity', '')
        weight = request.form.get('weight', '')
        notes = request.form.get('notes', '')
        
        # Insuline advies berekenen
        insulin_advice = calculate_insulin_advice(blood_value)
        
        conn = sqlite3.connect('mobile_diabetes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blood_readings 
            (user_id, date, time, blood_value, medication, activity, weight, notes, insulin_advice)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, time, blood_value, medication, activity, weight, notes, insulin_advice))
        
        conn.commit()
        conn.close()
        
        flash('Meting succesvol toegevoegd!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_reading.html')

@app.route('/history')
@login_required
def history():
    """Geschiedenis pagina"""
    user_id = session['user_id']
    
    # Filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    conn = sqlite3.connect('mobile_diabetes.db')
    cursor = conn.cursor()
    
    query = '''
        SELECT id, date, time, blood_value, medication, activity, weight, notes, insulin_advice
        FROM blood_readings 
        WHERE user_id = ?
    '''
    params = [user_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ' ORDER BY date DESC, time DESC'
    
    cursor.execute(query, params)
    readings = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', readings=readings)

@app.route('/analytics')
@login_required
def analytics():
    """Analytics pagina"""
    user_id = session['user_id']
    
    conn = sqlite3.connect('mobile_diabetes.db')
    cursor = conn.cursor()
    
    # Haal alle data op
    cursor.execute('''
        SELECT date, time, blood_value, medication, activity, weight
        FROM blood_readings 
        WHERE user_id = ?
        ORDER BY date, time
    ''', (user_id,))
    data = cursor.fetchall()
    conn.close()
    
    if len(data) < 3:
        return render_template('analytics.html', insufficient_data=True)
    
    # Converteer naar DataFrame voor analyse
    df = pd.DataFrame(data, columns=['date', 'time', 'blood_value', 'medication', 'activity', 'weight'])
    df['date'] = pd.to_datetime(df['date'])
    df['blood_value'] = pd.to_numeric(df['blood_value'])
    
    # Analytics
    analytics_data = {
        'total_readings': len(df),
        'avg_blood': df['blood_value'].mean(),
        'min_blood': df['blood_value'].min(),
        'max_blood': df['blood_value'].max(),
        'std_blood': df['blood_value'].std(),
        'high_risk_percentage': (df['blood_value'] > 180).mean() * 100,
        'low_risk_percentage': (df['blood_value'] < 70).mean() * 100,
        'stable_percentage': ((df['blood_value'] >= 70) & (df['blood_value'] <= 180)).mean() * 100
    }
    
    # Dagelijkse trends
    daily_avg = df.groupby(df['date'].dt.date)['blood_value'].mean()
    if len(daily_avg) > 1:
        analytics_data['trend'] = 'stijgend' if daily_avg.iloc[-1] > daily_avg.iloc[0] else 'dalend'
        analytics_data['trend_change'] = daily_avg.iloc[-1] - daily_avg.iloc[0]
    
    return render_template('analytics.html', analytics=analytics_data, data=df.to_dict('records'))

@app.route('/api/add_reading', methods=['POST'])
@login_required
def api_add_reading():
    """API endpoint voor het toevoegen van metingen"""
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        conn = sqlite3.connect('mobile_diabetes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blood_readings 
            (user_id, date, time, blood_value, medication, activity, weight, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, data['date'], data['time'], data['blood_value'], 
              data.get('medication', ''), data.get('activity', ''), 
              data.get('weight', ''), data.get('notes', '')))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Meting toegevoegd'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_readings')
@login_required
def api_get_readings():
    """API endpoint voor het ophalen van metingen"""
    user_id = session['user_id']
    
    conn = sqlite3.connect('mobile_diabetes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, time, blood_value, medication, activity, weight, notes
        FROM blood_readings 
        WHERE user_id = ?
        ORDER BY date DESC, time DESC
    ''', (user_id,))
    
    readings = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'readings': [
            {
                'date': r[0],
                'time': r[1],
                'blood_value': r[2],
                'medication': r[3],
                'activity': r[4],
                'weight': r[5],
                'notes': r[6]
            }
            for r in readings
        ]
    })

def calculate_insulin_advice(blood_value):
    """Bereken insuline advies"""
    if blood_value < 80:
        return "0 eenheden (laag risico)"
    elif 80 <= blood_value <= 120:
        return "2-3 eenheden"
    elif 121 <= blood_value <= 180:
        return "4-6 eenheden"
    elif 181 <= blood_value <= 250:
        return "6-8 eenheden"
    else:
        return "8+ eenheden (overleg arts)"

if __name__ == '__main__':
    # Initialiseer database
    init_mobile_database()
    
    # Start de app
    print("🚀 Diabetes Tracker Mobile App")
    print("=" * 40)
    print("📱 Open in je browser: http://localhost:5000")
    print("📱 Of scan de QR code met je telefoon")
    print("=" * 40)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 