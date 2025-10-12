from flask import Flask, jsonify, request, render_template_string, redirect, url_for, flash
import threading
import time
import uuid
from datetime import datetime
import logging
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Database configuration
DATABASE = 'email_tasks.db'

# Email configuration (UPDATE THESE WITH YOUR REAL EMAIL CREDENTIALS)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # For Gmail
    'smtp_port': 587,
    'sender_email': 'vijayamurugan27@gmail.com',  # Fixed: added @gmail.com
    'sender_password': 'zqca gsfr wcar bqwe'  # Your app password
}

# In-memory storage for task status
task_status: Dict[str, Dict] = {}

def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            email TEXT NOT NULL,
            status TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Email Marketing System</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: white; padding: 25px; margin: 10px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; margin: 5px; font-size: 14px; }
        .btn:hover { opacity: 0.9; }
        .btn-success { background: #28a745; }
        .btn-danger { background: #dc3545; }
        .btn-warning { background: #ffc107; color: black; }
        .status { padding: 5px 12px; border-radius: 20px; color: white; font-size: 12px; }
        .pending { background: #ffc107; }
        .running { background: #17a2b8; }
        .completed { background: #28a745; }
        .failed { background: #dc3545; }
        .task-info { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #007bff; color: white; }
        tr:hover { background: #f5f5f5; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .tab { overflow: hidden; border: 1px solid #ccc; background: #f1f1f1; border-radius: 6px 6px 0 0; }
        .tab button { background: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
        .tab button:hover { background: #ddd; }
        .tab button.active { background: #007bff; color: white; }
        .tabcontent { padding: 20px; border: 1px solid #ccc; border-top: none; border-radius: 0 0 6px 6px; background: white; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
</head>
<body>
    <h1>📧 Email Marketing System</h1>
    
    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="tab">
        <button class="tablink" onclick="openTab('emails', this)" id="defaultOpen">📋 Manage Emails</button>
        <button class="tablink" onclick="openTab('compose', this)">✉️ Compose & Send</button>
        <button class="tablink" onclick="openTab('tasks', this)">🚀 Task Monitor</button>
        <button class="tablink" onclick="openTab('logs', this)">📊 Email Logs</button>
    </div>

    <!-- Manage Emails Tab -->
    <div id="emails" class="tabcontent">
        <div class="container">
            <div class="card">
                <h2>➕ Add Email Address</h2>
                <form action="/add-email" method="POST">
                    <div class="form-group">
                        <label for="email">Email Address:</label>
                        <input type="email" id="email" name="email" required placeholder="example@domain.com">
                    </div>
                    <div class="form-group">
                        <label for="name">Name (Optional):</label>
                        <input type="text" id="name" name="name" placeholder="Recipient Name">
                    </div>
                    <button type="submit" class="btn">Add Email</button>
                </form>
                
                <hr style="margin: 20px 0;">
                
                <h3>📥 Add Multiple Emails</h3>
                <form action="/add-multiple-emails" method="POST">
                    <div class="form-group">
                        <label for="emails_text">Enter emails (one per line):</label>
                        <textarea id="emails_text" name="emails_text" rows="6" placeholder="user1@example.com&#10;user2@example.com&#10;user3@example.com"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">Add Multiple Emails</button>
                </form>
            </div>

            <div class="card">
                <h2>📧 Email List (Total: <span id="emailCount">0</span>)</h2>
                <div id="emailList">
                    Loading emails...
                </div>
            </div>
        </div>
    </div>

    <!-- Compose & Send Tab -->
    <div id="compose" class="tabcontent">
        <div class="card">
            <h2>✉️ Compose Bulk Email</h2>
            <form action="/start-email-task" method="POST">
                <div class="form-group">
                    <label for="subject">Subject:</label>
                    <input type="text" id="subject" name="subject" value="Greetings from Flask Application" required>
                </div>
                <div class="form-group">
                    <label for="message">Message:</label>
                    <textarea id="message" name="message" rows="6" required>Hello! This email was sent using Flask application. Thank you for subscribing!</textarea>
                </div>
                <button type="submit" class="btn btn-success">🚀 Send Bulk Email</button>
            </form>
            <button class="btn btn-warning" onclick="loadEmailStats()" style="margin-top: 10px;">📊 Refresh Stats</button>
        </div>

        <div class="stats" id="emailStats">
            <!-- Stats will be loaded here -->
        </div>
    </div>

    <!-- Task Monitor Tab -->
    <div id="tasks" class="tabcontent">
        <div class="card">
            <h2>📋 Active Tasks</h2>
            <div id="tasksList">
                <p>No active tasks</p>
            </div>
        </div>
    </div>

    <!-- Email Logs Tab -->
    <div id="logs" class="tabcontent">
        <div class="card">
            <h2>📊 Email Sending Logs</h2>
            <div id="emailLogs">
                Loading logs...
            </div>
        </div>
    </div>

    <script>
        function openTab(tabName, element) {
            var tabcontent = document.getElementsByClassName("tabcontent");
            for (var i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            
            var tablinks = document.getElementsByClassName("tablink");
            for (var i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            
            document.getElementById(tabName).style.display = "block";
            if (element) element.className += " active";
        }

        // Set default tab
        document.getElementById("defaultOpen").click();

        // Load initial data
        loadEmails();
        loadEmailStats();
        updateTaskList();
        loadEmailLogs();

        function loadEmails() {
            fetch('/emails')
                .then(response => response.json())
                .then(emails => {
                    const emailList = document.getElementById('emailList');
                    const emailCount = document.getElementById('emailCount');
                    
                    emailCount.textContent = emails.length;
                    
                    if (emails.length === 0) {
                        emailList.innerHTML = '<p>No emails found. Add some emails to get started.</p>';
                        return;
                    }

                    emailList.innerHTML = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>Name</th>
                                    <th>Added</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${emails.map(email => `
                                    <tr>
                                        <td>${email.email}</td>
                                        <td>${email.name || '-'}</td>
                                        <td>${new Date(email.created_at).toLocaleDateString()}</td>
                                        <td>
                                            <button class="btn btn-danger" onclick="deleteEmail(${email.id})">Delete</button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                });
        }

        function deleteEmail(emailId) {
            if (confirm('Are you sure you want to delete this email?')) {
                fetch(`/email/${emailId}`, { method: 'DELETE' })
                    .then(response => response.json())
                    .then(result => {
                        alert(result.message);
                        loadEmails();
                        loadEmailStats();
                    });
            }
        }

        function loadEmailStats() {
            fetch('/email-stats')
                .then(response => response.json())
                .then(stats => {
                    document.getElementById('emailStats').innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${stats.total_emails}</div>
                            <div>Total Emails</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.sent_today}</div>
                            <div>Sent Today</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${stats.total_sent}</div>
                            <div>Total Sent</div>
                        </div>
                    `;
                });
        }

        function updateTaskList() {
            fetch('/tasks')
                .then(response => response.json())
                .then(tasks => {
                    const tasksList = document.getElementById('tasksList');
                    if (tasks.length === 0) {
                        tasksList.innerHTML = '<p>No active tasks</p>';
                        return;
                    }

                    tasksList.innerHTML = tasks.map(task => `
                        <div class="task-info">
                            <h3>${task.name} <span class="status ${task.status}">${task.status.toUpperCase()}</span></h3>
                            <p><strong>ID:</strong> ${task.id}</p>
                            <p><strong>Started:</strong> ${task.start_time}</p>
                            <p><strong>Progress:</strong> ${task.progress}%</p>
                            ${task.result ? `<p><strong>Result:</strong> ${task.result}</p>` : ''}
                            ${task.status === 'running' ? `<p><strong>⏳ Running for:</strong> ${task.duration}s</p>` : ''}
                        </div>
                    `).join('');
                });
        }

        function loadEmailLogs() {
            fetch('/email-logs')
                .then(response => response.json())
                .then(logs => {
                    const logsContainer = document.getElementById('emailLogs');
                    
                    if (logs.length === 0) {
                        logsContainer.innerHTML = '<p>No email logs found.</p>';
                        return;
                    }

                    logsContainer.innerHTML = `
                        <table>
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>Status</th>
                                    <th>Sent At</th>
                                    <th>Error</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${logs.map(log => `
                                    <tr>
                                        <td>${log.email}</td>
                                        <td><span class="status ${log.status === 'sent' ? 'completed' : 'failed'}">${log.status}</span></td>
                                        <td>${new Date(log.sent_at).toLocaleString()}</td>
                                        <td>${log.error_message || '-'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    `;
                });
        }

        // Auto-refresh tasks and logs
        setInterval(() => {
            if (document.getElementById('tasks').style.display !== 'none') {
                updateTaskList();
            }
            if (document.getElementById('logs').style.display !== 'none') {
                loadEmailLogs();
            }
        }, 5000);
    </script>
</body>
</html>
'''

class EmailTaskManager:
    def __init__(self):
        self.tasks = {}

    def send_single_email(self, to_email: str, subject: str, message: str, task_id: str = None) -> bool:
        """Send a single email - REAL VERSION"""
        try:
            print(f"📧 Attempting to send email to: {to_email}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = EMAIL_CONFIG['sender_email']
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add message body
            body = message + "\n\n---\nSent via Flask Email Marketing System"
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            print(f"🔗 Connecting to SMTP server: {EMAIL_CONFIG['smtp_server']}:{EMAIL_CONFIG['smtp_port']}")
            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
            server.starttls()  # Enable security
            print("🔐 Logging in to email account...")
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            
            # Send email
            print("🚀 Sending email...")
            text = msg.as_string()
            server.sendmail(EMAIL_CONFIG['sender_email'], to_email, text)
            server.quit()
            
            print(f"✅ Email successfully sent to {to_email}")
            logger.info(f"✅ Email sent to {to_email}")
            return True

        except Exception as e:
            print(f"❌ FAILED to send email to {to_email}: {str(e)}")
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False

    def start_email_task(self, subject: str, message: str) -> str:
        """Start a bulk email task"""
        task_id = str(uuid.uuid4())
        
        task_status[task_id] = {
            "id": task_id,
            "name": f"📧 Bulk Email: {subject}",
            "type": "bulk_email",
            "status": "running",
            "progress": 0,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": None,
            "subject": subject,
            "message": message,
            "emails_processed": 0,
            "emails_total": 0,
            "emails_success": 0,
            "emails_failed": 0
        }

        thread = threading.Thread(
            target=self._send_bulk_emails,
            args=(task_id, subject, message),
            daemon=True
        )
        thread.start()

        logger.info(f"Started bulk email task {task_id}")
        return task_id

    def _send_bulk_emails(self, task_id: str, subject: str, message: str):
        """Send bulk emails to all recipients in database"""
        try:
            conn = get_db_connection()
            emails = conn.execute(
                'SELECT email, name FROM emails WHERE is_active = 1'
            ).fetchall()
            conn.close()

            total_emails = len(emails)
            task_status[task_id]["emails_total"] = total_emails

            if total_emails == 0:
                task_status[task_id].update({
                    "status": "completed",
                    "progress": 100,
                    "result": "No emails found in database"
                })
                logger.info("No emails found in database for sending")
                return

            logger.info(f"⏳ Starting bulk email send to {total_emails} recipients...")

            success_count = 0
            fail_count = 0

            for index, email_row in enumerate(emails):
                if task_status[task_id]["status"] == "cancelled":
                    break

                email = email_row['email']
                name = email_row['name']

                # Personalize message
                personalized_message = f"Hello {name},\n\n{message}" if name else message

                # Send email (REAL EMAIL SENDING)
                success = self.send_single_email(email, subject, personalized_message, task_id)

                # Update counts and log
                conn = get_db_connection()
                if success:
                    success_count += 1
                    conn.execute(
                        'INSERT INTO email_logs (task_id, email, status) VALUES (?, ?, ?)',
                        (task_id, email, 'sent')
                    )
                else:
                    fail_count += 1
                    conn.execute(
                        'INSERT INTO email_logs (task_id, email, status, error_message) VALUES (?, ?, ?, ?)',
                        (task_id, email, 'failed', 'SMTP error')
                    )
                conn.commit()
                conn.close()

                # Update progress
                progress = (index + 1) / total_emails * 100
                task_status[task_id]["progress"] = round(progress, 1)
                task_status[task_id]["emails_processed"] = index + 1
                task_status[task_id]["emails_success"] = success_count
                task_status[task_id]["emails_failed"] = fail_count

                # Small delay to avoid overwhelming SMTP server
                time.sleep(2)  # Increased delay to be safe with SMTP limits

            # Final update
            task_status[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": f"Sent {success_count}/{total_emails} emails successfully. Failed: {fail_count}"
            })
            logger.info(f"✅ Bulk email task {task_id} completed! Success: {success_count}, Failed: {fail_count}")

        except Exception as e:
            task_status[task_id].update({
                "status": "failed",
                "result": f"Bulk email failed: {str(e)}"
            })
            logger.error(f"❌ Bulk email task {task_id} failed: {str(e)}")

# Initialize task manager and database
email_manager = EmailTaskManager()
init_database()

@app.route('/')
def index():
    """Main page with email management UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/add-email', methods=['GET', 'POST'])
def add_email():
    """Add a new email to the database (supports both GET and POST)"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            name = request.form.get('name', '').strip()

            if not email:
                flash('Email is required', 'error')
                return redirect('/')

            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO emails (email, name) VALUES (?, ?)',
                    (email, name if name else None)
                )
                conn.commit()
                flash('Email added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Email already exists!', 'error')
            finally:
                conn.close()

            return redirect('/')
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect('/')
    
    else:
        # GET request - show the form
        return redirect('/')

@app.route('/add-multiple-emails', methods=['POST'])
def add_multiple_emails():
    """Add multiple emails at once"""
    try:
        emails_text = request.form.get('emails_text', '').strip()
        if not emails_text:
            flash('No emails provided', 'error')
            return redirect('/')
        
        emails = [email.strip() for email in emails_text.split('\n') if email.strip()]
        added_count = 0
        duplicate_count = 0
        
        conn = get_db_connection()
        for email in emails:
            if '@' in email:  # Basic email validation
                try:
                    conn.execute(
                        'INSERT INTO emails (email) VALUES (?)',
                        (email.lower(),)
                    )
                    added_count += 1
                except sqlite3.IntegrityError:
                    duplicate_count += 1
        conn.commit()
        conn.close()
        
        flash(f'Added {added_count} emails. {duplicate_count} duplicates skipped.', 'success')
        return redirect('/')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect('/')

@app.route('/emails', methods=['GET'])
def get_emails():
    """Get all emails from database"""
    conn = get_db_connection()
    emails = conn.execute(
        'SELECT * FROM emails WHERE is_active = 1 ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(email) for email in emails])

@app.route('/email/<int:email_id>', methods=['DELETE'])
def delete_email(email_id):
    """Delete an email from database"""
    conn = get_db_connection()
    conn.execute('UPDATE emails SET is_active = 0 WHERE id = ?', (email_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Email deleted successfully!"})

@app.route('/start-email-task', methods=['POST'])
def start_email_task():
    """Start a bulk email task"""
    try:
        subject = request.form.get('subject', 'Greetings from Flask Application')
        message = request.form.get('message', 'Hello! This email was sent using Flask application. Thank you for subscribing!')

        task_id = email_manager.start_email_task(subject, message)

        flash('Bulk email task started successfully! Check the Task Monitor tab for progress.', 'success')
        return redirect('/')

    except Exception as e:
        flash(f'Error starting email task: {str(e)}', 'error')
        return redirect('/')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get status of all tasks"""
    tasks = []
    for task_id, task_info in task_status.items():
        duration = None
        if task_info["status"] == "running":
            start_time = datetime.strptime(task_info["start_time"], "%Y-%m-%d %H:%M:%S")
            duration = int((datetime.now() - start_time).total_seconds())

        task_data = task_info.copy()
        task_data["duration"] = duration
        tasks.append(task_data)

    tasks.sort(key=lambda x: x["start_time"], reverse=True)
    return jsonify(tasks)

@app.route('/email-stats', methods=['GET'])
def get_email_stats():
    """Get email statistics"""
    conn = get_db_connection()
    
    total_emails = conn.execute('SELECT COUNT(*) FROM emails WHERE is_active = 1').fetchone()[0]
    
    today = datetime.now().strftime('%Y-%m-%d')
    sent_today = conn.execute(
        'SELECT COUNT(*) FROM email_logs WHERE DATE(sent_at) = ? AND status = "sent"', 
        (today,)
    ).fetchone()[0]
    
    total_sent = conn.execute(
        'SELECT COUNT(*) FROM email_logs WHERE status = "sent"'
    ).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "total_emails": total_emails,
        "sent_today": sent_today,
        "total_sent": total_sent
    })

@app.route('/email-logs', methods=['GET'])
def get_email_logs():
    """Get email sending logs"""
    conn = get_db_connection()
    logs = conn.execute(
        'SELECT * FROM email_logs ORDER BY sent_at DESC LIMIT 100'
    ).fetchall()
    conn.close()
    return jsonify([dict(log) for log in logs])

if __name__ == "__main__":
    print("🚀 Email Marketing System Started!")
    print("📧 REAL EMAIL SENDING ENABLED")
    print("🔧 Configuration:")
    print(f"   - SMTP Server: {EMAIL_CONFIG['smtp_server']}")
    print(f"   - Your Email: {EMAIL_CONFIG['sender_email']}")
    print("🌐 Access the dashboard at: http://localhost:5000")
    print("📍 To add emails: Go to 'Manage Emails' tab and use the form")
    
    app.run(debug=True, host='0.0.0.0', port=5000)