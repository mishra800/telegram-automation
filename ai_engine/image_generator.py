import os
from PIL import Image, ImageDraw, ImageFont
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

# Try to import optional dependencies
try:
    import torch
    from diffusers import StableDiffusionPipeline
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    logger.warning("Stable Diffusion not available, will use gradient fallback")

class ImageGenerator:
    def __init__(self):
        self.pipe = None
        if SD_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {self.device}")
        else:
            self.device = "cpu"
            logger.info("Using gradient-only mode")
        
    def _load_model(self):
        if not SD_AVAILABLE:
            return
        
        if self.pipe is None:
            try:
                logger.info("Loading Stable Diffusion model...")
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    Config.SD_MODEL,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.pipe = self.pipe.to(self.device)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading SD model: {e}")
                self.pipe = None
    
    def generate_image(self, topic, title):
        prompts = {
            'motivational': "inspiring sunrise, mountain peak, success journey, professional photography, vibrant colors",
            'tech_news': "futuristic technology, digital network, circuit board, modern tech aesthetic, blue and purple tones",
            'ai_updates': "artificial intelligence, neural network visualization, digital brain, tech innovation, glowing effects",
            'data_science': "data visualization, charts and graphs, analytics dashboard, professional business style",
            'productivity': "organized workspace, minimal desk setup, productivity tools, clean modern aesthetic"
        }
        
        prompt = prompts.get(topic, prompts['motivational'])
        
        try:
            if Config.USE_LOCAL_SD and SD_AVAILABLE:
                self._load_model()
                
                if self.pipe:
                    logger.info(f"Generating image for topic: {topic}")
                    image = self.pipe(
                        prompt,
                        num_inference_steps=30,
                        height=1024,
                        width=1024
                    ).images[0]
                else:
                    image = self._create_gradient_image(topic)
            else:
                image = self._create_gradient_image(topic)
            
            image_with_text = self._add_text_overlay(image, title, topic)
            
            filename = f"{topic}_{hash(title) % 10000}.png"
            filepath = os.path.join(Config.IMAGES_DIR, filename)
            image_with_text.save(filepath)
            
            logger.info(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._create_fallback_image(topic, title)
    
    def _create_gradient_image(self, topic):
        colors = {
            'motivational': [(255, 179, 71), (255, 107, 107)],
            'tech_news': [(67, 97, 238), (76, 201, 240)],
            'ai_updates': [(138, 43, 226), (75, 0, 130)],
            'data_science': [(34, 193, 195), (253, 187, 45)],
            'productivity': [(0, 180, 216), (0, 119, 182)]
        }
        
        color1, color2 = colors.get(topic, colors['motivational'])
        
        img = Image.new('RGB', (1080, 1080))
        draw = ImageDraw.Draw(img)
        
        for i in range(1080):
            r = int(color1[0] + (color2[0] - color1[0]) * i / 1080)
            g = int(color1[1] + (color2[1] - color1[1]) * i / 1080)
            b = int(color1[2] + (color2[2] - color1[2]) * i / 1080)
            draw.line([(0, i), (1080, i)], fill=(r, g, b))
        
        return img
    
    def _add_text_overlay(self, image, title, topic):
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        try:
            font_size = 80
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        words = title.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > 900:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        y_offset = 400
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            draw.text((x+2, y_offset+2), line, font=font, fill=(0, 0, 0))
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255))
            y_offset += 100
        
        return img
    
    def _create_fallback_image(self, topic, title):
        img = self._create_gradient_image(topic)
        img_with_text = self._add_text_overlay(img, title, topic)
        
        filename = f"{topic}_fallback_{hash(title) % 10000}.png"
        filepath = os.path.join(Config.IMAGES_DIR, filename)
        img_with_text.save(filepath)
        
        return filepath
