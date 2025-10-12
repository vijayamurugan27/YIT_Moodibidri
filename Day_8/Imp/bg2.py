from flask import Flask, jsonify, request, render_template_string
import threading
import time
import uuid
from datetime import datetime
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for task status (use database in production)
task_status: Dict[str, Dict] = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Background Task Manager</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-success { background: #28a745; }
        .status { padding: 5px 10px; border-radius: 4px; color: white; }
        .pending { background: #ffc107; }
        .running { background: #17a2b8; }
        .completed { background: #28a745; }
        .failed { background: #dc3545; }
        .task-info { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
    </style>
</head>
<body>
    <h1>🎯 Background Task Manager</h1>
    
    <div class="card">
        <h2>🚀 Start New Tasks</h2>
        <button class="btn" onclick="startTask('email')">📧 Send Bulk Emails</button>
        <button class="btn" onclick="startTask('report')">📊 Generate Report</button>
        <button class="btn" onclick="startTask('data')">🔄 Process Data</button>
        <button class="btn" onclick="startTask('cleanup')">🧹 Cleanup Files</button>
    </div>

    <div class="card">
        <h2>📋 Active Tasks</h2>
        <div id="tasksList">
            <p>No active tasks</p>
        </div>
    </div>

    <script>
        function startTask(type) {
            fetch('/start-task', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_type: type})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if(data.task_id) {
                    updateTaskList();
                    // Auto-refresh every 2 seconds for new tasks
                    setInterval(updateTaskList, 2000);
                }
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

        // Load tasks on page load
        updateTaskList();
    </script>
</body>
</html>
'''

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = {}

    def start_task(self, task_type: str, task_data: Dict = None) -> str:
        """Start a new background task and return its ID"""
        task_id = str(uuid.uuid4())
        
        # Define task based on type
        if task_type == "email":
            name = "📧 Bulk Email Sender"
            target = self._send_bulk_emails
        elif task_type == "report":
            name = "📊 Financial Report Generator"
            target = self._generate_report
        elif task_type == "data":
            name = "🔄 Data Processing"
            target = self._process_data
        elif task_type == "cleanup":
            name = "🧹 System Cleanup"
            target = self._cleanup_files
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # Initialize task status
        task_status[task_id] = {
            "id": task_id,
            "name": name,
            "type": task_type,
            "status": "running",
            "progress": 0,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": None,
            "data": task_data or {}
        }

        # Start the thread
        thread = threading.Thread(
            target=target,
            args=(task_id, task_data or {}),
            daemon=True
        )
        thread.start()

        logger.info(f"Started task {task_id}: {name}")
        return task_id

    def _send_bulk_emails(self, task_id: str, data: Dict):
        """Simulate sending bulk emails"""
        try:
            emails = data.get('emails', 100)
            logger.info(f"⏳ Starting bulk email send for {emails} emails...")
            
            for i in range(emails):
                if task_status[task_id]["status"] == "cancelled":
                    break
                    
                # Simulate email sending
                time.sleep(0.1)
                progress = (i + 1) / emails * 100
                task_status[task_id]["progress"] = round(progress, 1)
                
                # Simulate occasional failures
                if i == int(emails * 0.8):  # 80% through
                    logger.info("📨 Simulating email server delay...")
                    time.sleep(2)

            task_status[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": f"Successfully sent {emails} emails"
            })
            logger.info(f"✅ Bulk email task {task_id} completed!")

        except Exception as e:
            task_status[task_id].update({
                "status": "failed",
                "result": f"Failed: {str(e)}"
            })
            logger.error(f"❌ Email task {task_id} failed: {str(e)}")

    def _generate_report(self, task_id: str, data: Dict):
        """Simulate generating a complex report"""
        try:
            logger.info("⏳ Generating financial report...")
            
            steps = ["Collecting data", "Processing numbers", "Generating charts", "Creating PDF"]
            for i, step in enumerate(steps):
                if task_status[task_id]["status"] == "cancelled":
                    break
                    
                logger.info(f"📊 {step}...")
                time.sleep(1.5)
                task_status[task_id]["progress"] = (i + 1) / len(steps) * 100
                task_status[task_id]["result"] = f"Current: {step}"

            task_status[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": "Financial report generated: Q3-2024-Report.pdf"
            })
            logger.info(f"✅ Report generation {task_id} completed!")

        except Exception as e:
            task_status[task_id].update({
                "status": "failed",
                "result": f"Report generation failed: {str(e)}"
            })

    def _process_data(self, task_id: str, data: Dict):
        """Simulate data processing"""
        try:
            records = data.get('records', 500)
            logger.info(f"⏳ Processing {records} records...")
            
            for i in range(records):
                if task_status[task_id]["status"] == "cancelled":
                    break
                    
                if i % 50 == 0:  # Update progress every 50 records
                    progress = (i + 1) / records * 100
                    task_status[task_id]["progress"] = round(progress, 1)
                
                # Simulate record processing
                time.sleep(0.02)

            task_status[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": f"Processed {records} data records successfully"
            })
            logger.info(f"✅ Data processing {task_id} completed!")

        except Exception as e:
            task_status[task_id].update({
                "status": "failed",
                "result": f"Data processing failed: {str(e)}"
            })

    def _cleanup_files(self, task_id: str, data: Dict):
        """Simulate system cleanup"""
        try:
            logger.info("⏳ Starting system cleanup...")
            
            cleanup_tasks = [
                ("Cleaning temp files", 2),
                ("Optimizing database", 3),
                ("Removing old logs", 1),
                ("Clearing cache", 2)
            ]
            
            for i, (task_name, duration) in enumerate(cleanup_tasks):
                if task_status[task_id]["status"] == "cancelled":
                    break
                    
                logger.info(f"🧹 {task_name}...")
                task_status[task_id]["result"] = f"Current: {task_name}"
                
                for j in range(duration):
                    if task_status[task_id]["status"] == "cancelled":
                        break
                    time.sleep(1)
                    overall_progress = (i + (j + 1) / duration) / len(cleanup_tasks) * 100
                    task_status[task_id]["progress"] = round(overall_progress, 1)

            task_status[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": "System cleanup completed successfully"
            })
            logger.info(f"✅ Cleanup task {task_id} completed!")

        except Exception as e:
            task_status[task_id].update({
                "status": "failed",
                "result": f"Cleanup failed: {str(e)}"
            })

    def cancel_task(self, task_id: str):
        """Cancel a running task"""
        if task_id in task_status and task_status[task_id]["status"] == "running":
            task_status[task_id]["status"] = "cancelled"
            return True
        return False

# Initialize task manager
task_manager = BackgroundTaskManager()

@app.route('/')
def index():
    """Main page with task management UI"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/start-task', methods=['POST'])
def start_task():
    """Start a new background task"""
    try:
        data = request.get_json()
        task_type = data.get('task_type', 'email')
        
        task_id = task_manager.start_task(task_type, data)
        
        return jsonify({
            "message": f"Background task started successfully!",
            "task_id": task_id,
            "status": "running"
        }), 202
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get status of all tasks"""
    tasks = []
    for task_id, task_info in task_status.items():
        # Calculate duration for running tasks
        duration = None
        if task_info["status"] == "running":
            start_time = datetime.strptime(task_info["start_time"], "%Y-%m-%d %H:%M:%S")
            duration = int((datetime.now() - start_time).total_seconds())
        
        task_data = task_info.copy()
        task_data["duration"] = duration
        tasks.append(task_data)
    
    # Sort by start time (newest first)
    tasks.sort(key=lambda x: x["start_time"], reverse=True)
    return jsonify(tasks)

@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get status of a specific task"""
    if task_id not in task_status:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task_status[task_id])

@app.route('/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task"""
    if task_manager.cancel_task(task_id):
        return jsonify({"message": f"Task {task_id} cancelled successfully"})
    else:
        return jsonify({"error": "Task not found or not running"}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    active_tasks = sum(1 for task in task_status.values() if task["status"] == "running")
    
    return jsonify({
        "status": "healthy",
        "active_tasks": active_tasks,
        "total_tasks": len(task_status),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🚀 Background Task Manager Started!")
    print("📊 Access the dashboard at: http://localhost:5000")
    print("⏳ Tasks will run in the background while the server handles requests")
    app.run(debug=True, host='0.0.0.0', port=5000)