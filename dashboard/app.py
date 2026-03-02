from flask import Flask, render_template, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from analytics.database import AnalyticsDB
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

app = Flask(__name__)
db = AnalyticsDB()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    try:
        stats = db.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/topic-performance')
def get_topic_performance():
    try:
        performance = db.get_topic_performance(days=30)
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting topic performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/engagement-chart')
def get_engagement_chart():
    try:
        stats = db.get_dashboard_stats()
        daily_views = stats['daily_views']
        
        if not daily_views:
            return jsonify({'chart': None})
        
        dates = [dv[0] for dv in daily_views]
        views = [dv[1] for dv in daily_views]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, views, marker='o', linewidth=2, markersize=6)
        plt.title('Daily Views (Last 30 Days)', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Views', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        chart_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return jsonify({'chart': f'data:image/png;base64,{chart_data}'})
        
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return jsonify({'error': str(e)}), 500

def run_dashboard():
    logger.info(f"Starting dashboard on {Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}")
    app.run(
        host=Config.DASHBOARD_HOST,
        port=Config.DASHBOARD_PORT,
        debug=False
    )
