"""
A/B Testing System
Automatically tests content variations to optimize performance
"""

import sqlite3
import random
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class ABTester:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize A/B testing tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                variant_a_name TEXT NOT NULL,
                variant_b_name TEXT NOT NULL,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                winner TEXT,
                confidence REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ab_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                variant TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                views INTEGER DEFAULT 0,
                forwards INTEGER DEFAULT 0,
                reactions INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES ab_tests(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("A/B testing database initialized")
    
    def create_test(self, test_name, topic, variant_a_name, variant_b_name):
        """Create a new A/B test"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_tests (test_name, topic, variant_a_name, variant_b_name)
            VALUES (?, ?, ?, ?)
        ''', (test_name, topic, variant_a_name, variant_b_name))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created A/B test: {test_name} ({variant_a_name} vs {variant_b_name})")
        return test_id
    
    def get_active_tests(self, topic=None):
        """Get active A/B tests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if topic:
            cursor.execute('''
                SELECT id, test_name, topic, variant_a_name, variant_b_name
                FROM ab_tests
                WHERE status = 'active' AND topic = ?
            ''', (topic,))
        else:
            cursor.execute('''
                SELECT id, test_name, topic, variant_a_name, variant_b_name
                FROM ab_tests
                WHERE status = 'active'
            ''')
        
        tests = cursor.fetchall()
        conn.close()
        
        return tests
    
    def select_variant(self, test_id):
        """Randomly select variant A or B (50/50 split)"""
        return 'A' if random.random() < 0.5 else 'B'
    
    def record_result(self, test_id, variant, post_id, views, forwards, reactions):
        """Record A/B test result"""
        engagement_rate = ((forwards + reactions) / views * 100) if views > 0 else 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ab_results 
            (test_id, variant, post_id, views, forwards, reactions, engagement_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (test_id, variant, post_id, views, forwards, reactions, engagement_rate))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recorded A/B result: Test {test_id}, Variant {variant}, ER: {engagement_rate:.2f}%")
    
    def analyze_test(self, test_id, min_samples=20):
        """Analyze A/B test results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get results for both variants
        cursor.execute('''
            SELECT 
                variant,
                COUNT(*) as sample_size,
                AVG(views) as avg_views,
                AVG(forwards) as avg_forwards,
                AVG(reactions) as avg_reactions,
                AVG(engagement_rate) as avg_engagement
            FROM ab_results
            WHERE test_id = ?
            GROUP BY variant
        ''', (test_id,))
        
        results = {}
        for row in cursor.fetchall():
            results[row[0]] = {
                'sample_size': row[1],
                'avg_views': row[2],
                'avg_forwards': row[3],
                'avg_reactions': row[4],
                'avg_engagement': row[5]
            }
        
        conn.close()
        
        # Check if we have enough samples
        if not results or min(r['sample_size'] for r in results.values()) < min_samples:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least {min_samples} samples per variant'
            }
        
        # Determine winner based on engagement rate
        variant_a = results.get('A', {})
        variant_b = results.get('B', {})
        
        if not variant_a or not variant_b:
            return {
                'status': 'incomplete',
                'message': 'Missing data for one variant'
            }
        
        engagement_a = variant_a['avg_engagement']
        engagement_b = variant_b['avg_engagement']
        
        # Calculate improvement percentage
        if engagement_a > engagement_b:
            winner = 'A'
            improvement = ((engagement_a - engagement_b) / engagement_b * 100) if engagement_b > 0 else 100
        else:
            winner = 'B'
            improvement = ((engagement_b - engagement_a) / engagement_a * 100) if engagement_a > 0 else 100
        
        # Simple confidence calculation (simplified statistical test)
        sample_diff = abs(variant_a['sample_size'] - variant_b['sample_size'])
        engagement_diff = abs(engagement_a - engagement_b)
        
        # Confidence increases with larger sample size and larger difference
        confidence = min(
            (min(variant_a['sample_size'], variant_b['sample_size']) / min_samples) * 
            (engagement_diff / max(engagement_a, engagement_b)) * 100,
            99.9
        )
        
        return {
            'status': 'complete',
            'winner': winner,
            'improvement': improvement,
            'confidence': confidence,
            'variant_a': variant_a,
            'variant_b': variant_b
        }
    
    def conclude_test(self, test_id, winner, confidence):
        """Mark test as concluded"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE ab_tests
            SET status = 'concluded',
                end_date = ?,
                winner = ?,
                confidence = ?
            WHERE id = ?
        ''', (datetime.now(), winner, confidence, test_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Concluded test {test_id}: Winner = {winner}, Confidence = {confidence:.1f}%")
    
    def get_test_recommendations(self, topic):
        """Get recommendations based on concluded tests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                test_name,
                variant_a_name,
                variant_b_name,
                winner,
                confidence
            FROM ab_tests
            WHERE topic = ? AND status = 'concluded' AND confidence > 70
            ORDER BY end_date DESC
            LIMIT 5
        ''', (topic,))
        
        recommendations = []
        for row in cursor.fetchall():
            test_name, var_a, var_b, winner, confidence = row
            winning_variant = var_a if winner == 'A' else var_b
            
            recommendations.append({
                'test': test_name,
                'recommendation': f'Use {winning_variant}',
                'confidence': confidence
            })
        
        conn.close()
        return recommendations
    
    def auto_analyze_tests(self, min_samples=20):
        """Automatically analyze all active tests"""
        active_tests = self.get_active_tests()
        
        results = []
        for test in active_tests:
            test_id = test[0]
            test_name = test[1]
            
            analysis = self.analyze_test(test_id, min_samples)
            
            if analysis['status'] == 'complete' and analysis['confidence'] > 70:
                # Conclude the test
                self.conclude_test(
                    test_id,
                    analysis['winner'],
                    analysis['confidence']
                )
                
                results.append({
                    'test_id': test_id,
                    'test_name': test_name,
                    'winner': analysis['winner'],
                    'improvement': analysis['improvement'],
                    'confidence': analysis['confidence']
                })
        
        return results

# Pre-defined test scenarios
TEST_SCENARIOS = {
    'emoji_density': {
        'name': 'Emoji Density Test',
        'variant_a': 'Low emoji (1-2 per post)',
        'variant_b': 'High emoji (5-7 per post)'
    },
    'cta_style': {
        'name': 'CTA Style Test',
        'variant_a': 'Question CTA',
        'variant_b': 'Action CTA'
    },
    'content_length': {
        'name': 'Content Length Test',
        'variant_a': 'Short (3-5 bullets)',
        'variant_b': 'Long (7-10 bullets)'
    },
    'hashtag_count': {
        'name': 'Hashtag Count Test',
        'variant_a': 'Few hashtags (2-3)',
        'variant_b': 'Many hashtags (5-7)'
    },
    'title_style': {
        'name': 'Title Style Test',
        'variant_a': 'Direct title',
        'variant_b': 'Question title'
    }
}

def run_ab_analysis():
    """Scheduled task to analyze A/B tests"""
    tester = ABTester()
    results = tester.auto_analyze_tests(min_samples=20)
    
    if results:
        logger.info(f"A/B Analysis complete: {len(results)} tests concluded")
        for result in results:
            logger.info(
                f"Test '{result['test_name']}': "
                f"Winner = {result['winner']}, "
                f"Improvement = {result['improvement']:.1f}%, "
                f"Confidence = {result['confidence']:.1f}%"
            )
    else:
        logger.info("A/B Analysis: No tests ready for conclusion")
    
    return results

if __name__ == "__main__":
    # Test the A/B testing system
    tester = ABTester()
    
    # Create a test
    test_id = tester.create_test(
        test_name="Emoji Density Test",
        topic="motivational",
        variant_a_name="Low emoji (1-2)",
        variant_b_name="High emoji (5-7)"
    )
    
    print(f"Created test ID: {test_id}")
    
    # Simulate some results
    for i in range(25):
        variant = tester.select_variant(test_id)
        views = random.randint(100, 500)
        forwards = random.randint(5, 50) if variant == 'B' else random.randint(2, 30)
        reactions = random.randint(10, 80) if variant == 'B' else random.randint(5, 50)
        
        tester.record_result(test_id, variant, i, views, forwards, reactions)
    
    # Analyze
    analysis = tester.analyze_test(test_id, min_samples=10)
    print(f"\nAnalysis: {analysis}")
    
    if analysis['status'] == 'complete':
        tester.conclude_test(test_id, analysis['winner'], analysis['confidence'])
        print(f"\nTest concluded: Winner = {analysis['winner']}")
