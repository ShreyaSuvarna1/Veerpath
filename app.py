from flask import Flask, render_template, abort
from flask_apscheduler import APScheduler
from scraper import scrape_all_jobs, save_jobs, load_jobs
import atexit
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)

# Global variables
cached_jobs = []
last_updated = None

def initialize_app():
    """Initialize application resources"""
    global cached_jobs, last_updated
    
    # Ensure required directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    try:
        cached_jobs = load_jobs()
        if cached_jobs:
            last_updated = datetime.now()
            app.logger.info(f"Loaded {len(cached_jobs)} cached jobs")
        else:
            refresh_jobs()
    except Exception as e:
        app.logger.error(f"Initialization failed: {str(e)}")
        cached_jobs = []
        refresh_jobs()

def refresh_jobs():
    """Refresh the job cache"""
    global cached_jobs, last_updated
    try:
        app.logger.info("Starting job refresh...")
        new_jobs = scrape_all_jobs()
        cached_jobs = new_jobs
        save_jobs(cached_jobs)
        last_updated = datetime.now()
        app.logger.info(f"Successfully updated {len(cached_jobs)} jobs")
        return True
    except Exception as e:
        app.logger.error(f"Job refresh failed: {str(e)}")
        return False

# Scheduled job every 30 minutes
@scheduler.task('interval', id='scheduled_refresh', minutes=30)
def scheduled_refresh():
    refresh_jobs()

@app.route('/')
def home():
    """Main application route"""
    try:
        app.logger.info(f"Serving {len(cached_jobs)} jobs")
        return render_template("profile.html",
                            jobs=cached_jobs,
                            last_updated=last_updated)
    except Exception as e:
        app.logger.error(f"Template rendering failed: {str(e)}")
        abort(500, description="Failed to load page")

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'job_count': len(cached_jobs),
        'last_updated': last_updated.isoformat() if last_updated else None,
        'services': ['scheduler' if scheduler.running else 'inactive']
    }

# Shutdown handler
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Start scheduler
    scheduler.start()
    
    # Run application
    app.run(debug=True, host='0.0.0.0')
    