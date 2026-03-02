import ollama
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class ContentGenerator:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.host = Config.OLLAMA_HOST
        self.use_gemini = Config.USE_GEMINI
        self.gemini_api_key = Config.GEMINI_API_KEY
        
        if self.use_gemini and self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini Pro initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Gemini: {e}")
                self.use_gemini = False
        
    def generate_content(self, topic):
        prompts = {
            'motivational': """Generate a motivational post for social media with:
- A catchy headline (max 10 words)
- 5-7 short bullet points with actionable advice
- A call-to-action line
- 3-5 relevant hashtags
Keep it inspiring and practical.""",
            
            'tech_news': """Generate a tech news summary post with:
- A catchy headline about latest tech trends
- 5-7 bullet points covering recent developments
- A thought-provoking question as CTA
- 3-5 tech-related hashtags
Focus on AI, cloud, or software development.""",
            
            'ai_updates': """Generate an AI industry update post with:
- A compelling headline about AI advancements
- 5-7 bullet points on recent AI breakthroughs
- A call-to-action encouraging discussion
- 3-5 AI-related hashtags
Make it informative yet accessible.""",
            
            'data_science': """Generate a data science tips post with:
- A catchy headline about data science
- 5-7 practical tips or insights
- A call-to-action for learning
- 3-5 data science hashtags
Focus on practical skills and tools.""",
            
            'productivity': """Generate a productivity tips post with:
- A catchy headline about productivity
- 5-7 actionable productivity hacks
- A motivating call-to-action
- 3-5 productivity hashtags
Keep it practical and easy to implement."""
        }
        
        prompt = prompts.get(topic, prompts['motivational'])
        
        try:
            logger.info(f"Generating content for topic: {topic}")
            
            # Try Gemini first if enabled
            if self.use_gemini and self.gemini_api_key:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    content = response.text
                    logger.info(f"Content generated successfully with Gemini for {topic}")
                    return self._format_content(content, topic)
                except Exception as e:
                    logger.warning(f"Gemini failed, trying Ollama: {e}")
            
            # Fallback to Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }]
            )
            
            content = response['message']['content']
            logger.info(f"Content generated successfully with Ollama for {topic}")
            return self._format_content(content, topic)
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return self._get_fallback_content(topic)
    
    def _format_content(self, content, topic):
        lines = content.strip().split('\n')
        formatted = '\n'.join([line for line in lines if line.strip()])
        return {
            'text': formatted,
            'topic': topic
        }
    
    def _get_fallback_content(self, topic):
        fallbacks = {
            'motivational': """🌟 Start Your Day with Purpose

• Set clear goals before you begin
• Focus on progress, not perfection
• Celebrate small wins daily
• Stay consistent with your habits
• Believe in your potential

Take action today! What's your first step?

#Motivation #Success #GrowthMindset #DailyInspiration #Goals""",
            
            'tech_news': """🚀 Tech Trends This Week

• AI models getting more efficient
• Cloud computing costs decreasing
• Open-source tools gaining traction
• Developer productivity tools evolving
• Cybersecurity remains top priority

What tech trend excites you most?

#TechNews #AI #CloudComputing #Development #Innovation""",
            
            'ai_updates': """🤖 AI Industry Highlights

• Large language models improving rapidly
• AI automation transforming workflows
• Open-source AI democratizing access
• Ethical AI gaining importance
• AI tools becoming more accessible

How are you using AI in your work?

#AI #MachineLearning #ArtificialIntelligence #Tech #Innovation""",
            
            'data_science': """📊 Data Science Pro Tips

• Master SQL before fancy algorithms
• Clean data beats complex models
• Visualize before you analyze
• Document your analysis process
• Learn statistics fundamentals

What's your favorite data science tool?

#DataScience #Analytics #Python #MachineLearning #BigData""",
            
            'productivity': """⚡ Productivity Power-Ups

• Use the 2-minute rule for quick tasks
• Batch similar tasks together
• Take regular breaks (Pomodoro)
• Eliminate distractions first
• Review and plan weekly

What's your best productivity hack?

#Productivity #TimeManagement #Efficiency #WorkSmart #Success"""
        }
        
        return {
            'text': fallbacks.get(topic, fallbacks['motivational']),
            'topic': topic
        }
