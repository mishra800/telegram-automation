from datetime import datetime
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

# Try to import ollama (optional for cloud deployment)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available, will use Gemini or fallback content")

class ContentGenerator:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        self.host = Config.OLLAMA_HOST
        self.use_gemini = Config.USE_GEMINI
        self.gemini_api_key = Config.GEMINI_API_KEY
        
        if self.use_gemini and self.gemini_api_key:
            try:
                import google.genai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini Pro initialized successfully")
            except ImportError:
                # Fallback to old package if new one not available
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.gemini_api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    logger.info("Gemini Pro initialized successfully (legacy package)")
                except Exception as e:
                    logger.error(f"Error initializing Gemini: {e}")
                    self.use_gemini = False
            except Exception as e:
                logger.error(f"Error initializing Gemini: {e}")
                self.use_gemini = False
        
    def generate_content(self, topic, trending_keywords=None, funnel_stage='value'):
        """Generate content with context awareness and uniqueness"""
        
        # Add context for better uniqueness
        current_date = datetime.now().strftime("%B %Y")
        trending_context = f"Trending: {', '.join(trending_keywords[:3])}" if trending_keywords else ""
        
        # Stage-specific content guidelines
        stage_instructions = {
            'viral': "Make it controversial, emotional, or surprising. Use pattern interrupts.",
            'value': "Provide actionable, practical value. Be specific with numbers and examples.",
            'authority': "Include data, case studies, or expert insights. Build credibility.",
            'soft_promotion': "Tell a relatable story about a problem. Hint at solutions naturally.",
            'strong_cta': "Focus on transformation and urgency. Clear benefits and social proof."
        }
        
        stage_guide = stage_instructions.get(funnel_stage, stage_instructions['value'])
        
        prompts = {
            'motivational': f"""Generate a UNIQUE motivational post for {current_date}. {trending_context}

REQUIREMENTS:
- Hook: Start with a surprising fact, question, or bold statement
- Story: Include a micro-story or specific example (not generic advice)
- Value: 3-5 specific, actionable steps with numbers/metrics
- Emotion: Use power words that trigger emotion
- CTA: End with a thought-provoking question or challenge
- Hashtags: 3-5 trending + niche hashtags

STAGE FOCUS: {stage_guide}

AVOID: Generic advice, clichés, overused phrases
TONE: Conversational, authentic, slightly provocative
LENGTH: 150-250 words""",
            
            'tech_news': f"""Generate a UNIQUE tech news post for {current_date}. {trending_context}

REQUIREMENTS:
- Hook: Start with "Breaking:" or surprising stat about recent tech development
- Context: Explain WHY this matters (not just what happened)
- Impact: 3-4 specific implications for developers/businesses
- Insight: Add a contrarian or unique perspective
- CTA: Ask for predictions or opinions
- Hashtags: Mix trending tech + niche tags

STAGE FOCUS: {stage_guide}

AVOID: Press release language, obvious observations
TONE: Insider knowledge, analytical, forward-thinking
LENGTH: 150-250 words""",
            
            'ai_updates': f"""Generate a UNIQUE AI industry post for {current_date}. {trending_context}

REQUIREMENTS:
- Hook: Start with a mind-blowing AI capability or prediction
- Breakdown: Explain complex AI concept in simple terms with analogy
- Applications: 3-4 specific real-world use cases with examples
- Controversy: Address a debate or ethical consideration
- CTA: Ask how readers are using AI or their concerns
- Hashtags: Mix AI trends + specific tools/models

STAGE FOCUS: {stage_guide}

AVOID: Hype without substance, fear-mongering
TONE: Informed, balanced, practical
LENGTH: 150-250 words""",
            
            'data_science': f"""Generate a UNIQUE data science post for {current_date}. {trending_context}

REQUIREMENTS:
- Hook: Start with a counterintuitive data insight or mistake
- Lesson: Share a specific technique/approach with code concept
- Example: Include a real-world scenario or case study
- Tools: Mention 2-3 specific tools/libraries with use cases
- CTA: Ask about readers' biggest data challenge
- Hashtags: Mix data science + specific tools

STAGE FOCUS: {stage_guide}

AVOID: Textbook definitions, obvious tips
TONE: Experienced practitioner, helpful, technical but accessible
LENGTH: 150-250 words""",
            
            'productivity': f"""Generate a UNIQUE productivity post for {current_date}. {trending_context}

REQUIREMENTS:
- Hook: Start with a productivity myth or surprising research finding
- Framework: Share a specific system/method with clear steps
- Science: Include psychological principle or research backing
- Example: Show before/after or specific results
- CTA: Challenge readers to try it for X days
- Hashtags: Mix productivity + specific methods

STAGE FOCUS: {stage_guide}

AVOID: Generic "wake up early" advice, obvious tips
TONE: Science-backed, practical, results-focused
LENGTH: 150-250 words"""
        }
        
        prompt = prompts.get(topic, prompts['motivational'])
        
        try:
            logger.info(f"Generating content for topic: {topic}, stage: {funnel_stage}")
            
            # Try Gemini first if enabled
            if self.use_gemini and self.gemini_api_key:
                try:
                    response = self.gemini_model.generate_content(prompt)
                    content = response.text
                    logger.info(f"Content generated successfully with Gemini for {topic}")
                    return self._format_content(content, topic)
                except Exception as e:
                    logger.warning(f"Gemini failed, trying Ollama: {e}")
            
            # Fallback to Ollama if available
            if OLLAMA_AVAILABLE:
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
            else:
                logger.info(f"Ollama not available, using fallback content for {topic}")
                return self._get_fallback_content(topic)
            
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
