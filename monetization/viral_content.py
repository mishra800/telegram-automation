import random
from datetime import datetime
from bot.logger import setup_logger

logger = setup_logger(__name__)

class ViralContentEngine:
    """Creates viral, engaging content templates"""
    
    def __init__(self):
        self.viral_templates = {
            'question': [
                "🤔 Quick Question:\n{question}\n\nComment below! 👇",
                "💭 Let's discuss:\n{question}\n\nWhat's your take?",
                "🎯 Your opinion matters:\n{question}\n\nDrop your thoughts!"
            ],
            'challenge': [
                "🔥 7-Day Challenge:\n{challenge}\n\nWho's in? Tag a friend!",
                "💪 Challenge Accepted?\n{challenge}\n\nShare your progress!",
                "🚀 Ready for this?\n{challenge}\n\nLet's do it together!"
            ],
            'poll': [
                "📊 Quick Poll:\n{question}\n\nA) {option_a}\nB) {option_b}\n\nVote in comments!",
                "🗳️ You decide:\n{question}\n\n👍 for {option_a}\n❤️ for {option_b}",
                "⚡ Fast poll:\n{question}\n\nReact to vote!"
            ],
            'tag_friend': [
                "👥 Tag someone who needs to see this!\n\n{content}",
                "📢 Share this with a friend who {reason}!\n\n{content}",
                "💬 Tag 3 friends who should know this!\n\n{content}"
            ],
            'story': [
                "📖 Real Story:\n\n{story}\n\nWhat would you do?",
                "💡 Lesson learned:\n\n{story}\n\nYour thoughts?",
                "🎯 Success story:\n\n{story}\n\nInspired?"
            ]
        }
        
        self.engagement_boosters = [
            "\n\n💬 Comment your answer!",
            "\n\n👇 Drop your thoughts below!",
            "\n\n🔥 Share if you agree!",
            "\n\n💪 Tag someone who needs this!",
            "\n\n⚡ Save this for later!",
            "\n\n🎯 Which one are you? Comment!"
        ]
        
        self.viral_questions = {
            'tech_news': [
                "Which tech trend will dominate 2026?",
                "AI or Blockchain - which is more important?",
                "What's the next big tech innovation?",
                "Remote work or office - what's better?"
            ],
            'ai_updates': [
                "Will AI replace your job?",
                "ChatGPT or Gemini - which is better?",
                "Should AI be regulated?",
                "What's your favorite AI tool?"
            ],
            'productivity': [
                "Morning person or night owl?",
                "What's your #1 productivity hack?",
                "Coffee or tea for focus?",
                "How many hours do you work daily?"
            ],
            'data_science': [
                "Python or R for data science?",
                "What's the hardest part of data science?",
                "SQL or NoSQL - which do you prefer?",
                "Favorite data visualization tool?"
            ],
            'motivational': [
                "What motivates you to wake up?",
                "Biggest challenge you overcame?",
                "Your definition of success?",
                "Best advice you ever received?"
            ]
        }
    
    def create_engagement_post(self, topic, post_type='question'):
        """Create a viral engagement post"""
        
        if post_type == 'question':
            questions = self.viral_questions.get(topic, self.viral_questions['motivational'])
            question = random.choice(questions)
            template = random.choice(self.viral_templates['question'])
            content = template.format(question=question)
        
        elif post_type == 'poll':
            content = self._create_poll(topic)
        
        elif post_type == 'challenge':
            content = self._create_challenge(topic)
        
        else:
            content = self._create_tag_friend_post(topic)
        
        # Add engagement booster
        content += random.choice(self.engagement_boosters)
        
        logger.info(f"Created {post_type} engagement post for {topic}")
        return content
    
    def _create_poll(self, topic):
        """Create a poll post"""
        polls = {
            'tech_news': {
                'question': "Best programming language for 2026?",
                'option_a': "Python",
                'option_b': "JavaScript"
            },
            'ai_updates': {
                'question': "AI will be mostly used for?",
                'option_a': "Content Creation",
                'option_b': "Automation"
            },
            'productivity': {
                'question': "Best time to work?",
                'option_a': "Morning (6-12)",
                'option_b': "Night (6-12)"
            }
        }
        
        poll_data = polls.get(topic, polls['tech_news'])
        template = random.choice(self.viral_templates['poll'])
        return template.format(**poll_data)
    
    def _create_challenge(self, topic):
        """Create a challenge post"""
        challenges = {
            'productivity': "Wake up at 5 AM for 7 days straight",
            'tech_news': "Learn a new tech skill this week",
            'ai_updates': "Use AI tools for all your work today",
            'data_science': "Complete one data project this week",
            'motivational': "Do something that scares you daily"
        }
        
        challenge = challenges.get(topic, challenges['motivational'])
        template = random.choice(self.viral_templates['challenge'])
        return template.format(challenge=challenge)
    
    def _create_tag_friend_post(self, topic):
        """Create a tag-a-friend post"""
        reasons = {
            'tech_news': "loves technology",
            'ai_updates': "needs to try AI tools",
            'productivity': "wants to be more productive",
            'data_science': "is learning data science",
            'motivational': "needs motivation today"
        }
        
        reason = reasons.get(topic, "should see this")
        content = f"Amazing {topic.replace('_', ' ')} insight!"
        template = random.choice(self.viral_templates['tag_friend'])
        return template.format(content=content, reason=reason)
    
    def add_viral_elements(self, content, topic):
        """Add viral elements to existing content"""
        # Add emojis
        content = self._add_emojis(content, topic)
        
        # Add engagement CTA
        if random.random() < 0.5:
            content += random.choice(self.engagement_boosters)
        
        return content
    
    def _add_emojis(self, content, topic):
        """Add relevant emojis to content"""
        emoji_map = {
            'tech_news': ['💻', '🚀', '⚡', '🔥', '💡'],
            'ai_updates': ['🤖', '🧠', '⚡', '🎯', '💫'],
            'productivity': ['⚡', '💪', '🎯', '🔥', '⏰'],
            'data_science': ['📊', '📈', '🔍', '💡', '🎯'],
            'motivational': ['💪', '🌟', '🔥', '⚡', '🎯']
        }
        
        emojis = emoji_map.get(topic, emoji_map['motivational'])
        # Add emoji to first line if not present
        lines = content.split('\n')
        if lines and not any(emoji in lines[0] for emoji in emojis):
            lines[0] = f"{random.choice(emojis)} {lines[0]}"
        
        return '\n'.join(lines)
