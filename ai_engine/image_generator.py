import os
import random
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
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
        
        # Multiple gradient palettes per topic
        self.gradient_palettes = {
            'motivational': [
                [(255, 179, 71), (255, 107, 107)],   # Orange to Red
                [(255, 94, 77), (251, 194, 235)],    # Coral to Pink
                [(254, 140, 0), (248, 54, 0)],       # Sunset
                [(255, 200, 124), (252, 251, 121)],  # Golden
                [(243, 144, 79), (59, 67, 113)]      # Warm to Cool
            ],
            'tech_news': [
                [(67, 97, 238), (76, 201, 240)],     # Blue gradient
                [(13, 27, 42), (27, 43, 52)],        # Dark tech
                [(0, 180, 219), (0, 131, 176)],      # Cyan
                [(30, 60, 114), (42, 82, 152)],      # Deep blue
                [(72, 52, 212), (130, 119, 255)]     # Purple tech
            ],
            'ai_updates': [
                [(138, 43, 226), (75, 0, 130)],      # Purple
                [(159, 18, 255), (231, 74, 59)],     # Purple to Red
                [(102, 126, 234), (118, 75, 162)],   # Violet
                [(79, 172, 254), (0, 242, 254)],     # Electric blue
                [(195, 55, 100), (29, 38, 113)]      # Pink to Navy
            ],
            'data_science': [
                [(34, 193, 195), (253, 187, 45)],    # Teal to Yellow
                [(0, 198, 255), (0, 114, 255)],      # Blue data
                [(19, 84, 122), (128, 208, 199)],    # Ocean
                [(52, 143, 80), (86, 180, 211)],     # Green to Blue
                [(255, 75, 145), (255, 200, 55)]     # Pink to Yellow
            ],
            'productivity': [
                [(0, 180, 216), (0, 119, 182)],      # Blue
                [(108, 92, 231), (192, 108, 132)],   # Purple to Pink
                [(76, 161, 175), (196, 224, 229)],   # Calm blue
                [(30, 150, 252), (142, 209, 252)],   # Sky blue
                [(99, 179, 237), (6, 190, 182)]      # Aqua
            ]
        }
        
        # Gradient directions
        self.gradient_directions = [
            'vertical',      # Top to bottom
            'horizontal',    # Left to right
            'diagonal_lr',   # Top-left to bottom-right
            'diagonal_rl',   # Top-right to bottom-left
            'radial'         # Center outward
        ]
        
        # Text positions
        self.text_positions = [
            'center',        # Middle of image
            'top_third',     # Upper third
            'bottom_third'   # Lower third
        ]
    
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
        """Generate unique image with random variations"""
        # Generate random seed for uniqueness
        seed = random.randint(0, 2147483647)
        random.seed(seed)
        np.random.seed(seed)
        
        logger.info(f"Generating image for topic: {topic} with seed: {seed}")
        
        try:
            if Config.USE_LOCAL_SD and SD_AVAILABLE:
                image = self._generate_sd_image(topic, seed)
            else:
                image = self._create_gradient_image(topic)
            
            # Add text overlay with variations
            image_with_text = self._add_text_overlay(image, title, topic)
            
            # Add subtle noise texture
            image_with_texture = self._add_noise_texture(image_with_text)
            
            # Add watermark with date
            final_image = self._add_watermark(image_with_texture)
            
            # Save with UUID filename
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(Config.IMAGES_DIR, filename)
            final_image.save(filepath, 'PNG', quality=95)
            
            logger.info(f"Image saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating image: {e}", exc_info=True)
            return self._create_fallback_image(topic, title)
    
    def _generate_sd_image(self, topic, seed):
        """Generate image using Stable Diffusion with dynamic prompts"""
        self._load_model()
        
        if not self.pipe:
            return self._create_gradient_image(topic)
        
        # Dynamic prompts with 2026 trending styles
        base_prompts = {
            'motivational': "inspiring motivational poster, success mindset, powerful energy",
            'tech_news': "futuristic technology interface, digital innovation, tech breakthrough",
            'ai_updates': "artificial intelligence visualization, neural network, AI innovation",
            'data_science': "data analytics visualization, modern dashboard, insights",
            'productivity': "productivity workspace, organized efficiency, focus"
        }
        
        base = base_prompts.get(topic, base_prompts['motivational'])
        
        # Add trending 2026 design elements
        style_elements = [
            "trending 2026 design",
            "cinematic lighting",
            "ultra sharp",
            "vibrant modern social media style",
            "professional photography",
            "8k resolution",
            "dramatic composition",
            "award winning design"
        ]
        
        # Randomly select 3-4 style elements
        selected_styles = random.sample(style_elements, random.randint(3, 4))
        full_prompt = f"{base}, {', '.join(selected_styles)}"
        
        logger.info(f"SD Prompt: {full_prompt}")
        
        try:
            # Set seed for reproducibility
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            image = self.pipe(
                full_prompt,
                num_inference_steps=30,
                height=1080,
                width=1080,
                generator=generator
            ).images[0]
            
            return image
        except Exception as e:
            logger.error(f"SD generation failed: {e}")
            return self._create_gradient_image(topic)
    
    def _create_gradient_image(self, topic):
        """Create gradient image with random palette and direction"""
        # Select random palette for this topic
        palettes = self.gradient_palettes.get(topic, self.gradient_palettes['motivational'])
        color1, color2 = random.choice(palettes)
        
        # Select random gradient direction
        direction = random.choice(self.gradient_directions)
        
        logger.info(f"Creating {direction} gradient: {color1} -> {color2}")
        
        img = Image.new('RGB', (1080, 1080))
        draw = ImageDraw.Draw(img)
        
        if direction == 'vertical':
            # Top to bottom
            for i in range(1080):
                r = int(color1[0] + (color2[0] - color1[0]) * i / 1080)
                g = int(color1[1] + (color2[1] - color1[1]) * i / 1080)
                b = int(color1[2] + (color2[2] - color1[2]) * i / 1080)
                draw.line([(0, i), (1080, i)], fill=(r, g, b))
        
        elif direction == 'horizontal':
            # Left to right
            for i in range(1080):
                r = int(color1[0] + (color2[0] - color1[0]) * i / 1080)
                g = int(color1[1] + (color2[1] - color1[1]) * i / 1080)
                b = int(color1[2] + (color2[2] - color1[2]) * i / 1080)
                draw.line([(i, 0), (i, 1080)], fill=(r, g, b))
        
        elif direction == 'diagonal_lr':
            # Top-left to bottom-right
            for i in range(1080):
                for j in range(1080):
                    progress = (i + j) / (1080 * 2)
                    r = int(color1[0] + (color2[0] - color1[0]) * progress)
                    g = int(color1[1] + (color2[1] - color1[1]) * progress)
                    b = int(color1[2] + (color2[2] - color1[2]) * progress)
                    draw.point((j, i), fill=(r, g, b))
        
        elif direction == 'diagonal_rl':
            # Top-right to bottom-left
            for i in range(1080):
                for j in range(1080):
                    progress = (i + (1080 - j)) / (1080 * 2)
                    r = int(color1[0] + (color2[0] - color1[0]) * progress)
                    g = int(color1[1] + (color2[1] - color1[1]) * progress)
                    b = int(color1[2] + (color2[2] - color1[2]) * progress)
                    draw.point((j, i), fill=(r, g, b))
        
        elif direction == 'radial':
            # Center outward
            center_x, center_y = 540, 540
            max_distance = 540 * 1.414  # Diagonal distance
            
            for i in range(1080):
                for j in range(1080):
                    distance = ((j - center_x) ** 2 + (i - center_y) ** 2) ** 0.5
                    progress = min(distance / max_distance, 1.0)
                    r = int(color1[0] + (color2[0] - color1[0]) * progress)
                    g = int(color1[1] + (color2[1] - color1[1]) * progress)
                    b = int(color1[2] + (color2[2] - color1[2]) * progress)
                    draw.point((j, i), fill=(r, g, b))
        
        return img
    
    def _add_text_overlay(self, image, title, topic):
        """Add text with dynamic positioning and sizing"""
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Dynamic font sizing based on text length
        text_length = len(title)
        if text_length < 30:
            font_size = 90
        elif text_length < 50:
            font_size = 75
        elif text_length < 70:
            font_size = 65
        else:
            font_size = 55
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
            small_font = ImageFont.truetype("arial.ttf", font_size // 2)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
                small_font = ImageFont.truetype("Arial.ttf", font_size // 2)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
        
        # Word wrap
        words = title.split()
        lines = []
        current_line = []
        max_width = 950
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Limit to 4 lines
        lines = lines[:4]
        
        # Random text position
        position = random.choice(self.text_positions)
        
        if position == 'center':
            y_start = 540 - (len(lines) * (font_size + 20)) // 2
        elif position == 'top_third':
            y_start = 200
        else:  # bottom_third
            y_start = 1080 - 300 - (len(lines) * (font_size + 20))
        
        logger.info(f"Text position: {position}, font size: {font_size}")
        
        # Draw text with shadow
        y_offset = y_start
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1080 - text_width) // 2
            
            # Shadow (offset by 3 pixels)
            draw.text((x+3, y_offset+3), line, font=font, fill=(0, 0, 0, 180))
            # Main text
            draw.text((x, y_offset), line, font=font, fill=(255, 255, 255))
            y_offset += font_size + 20
        
        return img
    
    def _add_noise_texture(self, image):
        """Add subtle noise overlay for texture"""
        img = image.copy()
        
        # Create noise layer
        noise = np.random.randint(0, 25, (1080, 1080, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise, mode='RGB')
        
        # Blend with original (very subtle - 5% opacity)
        img = Image.blend(img, noise_img, alpha=0.05)
        
        return img
    
    def _add_watermark(self, image):
        """Add watermark with current date"""
        img = image.copy()
        draw = ImageDraw.Draw(img)
        
        # Get current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        watermark_text = f"© {date_str}"
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # Position at bottom-right corner
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = 1080 - text_width - 20
        y = 1080 - text_height - 20
        
        # Semi-transparent watermark
        draw.text((x+1, y+1), watermark_text, font=font, fill=(0, 0, 0, 100))
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 150))
        
        return img
    
    def _create_fallback_image(self, topic, title):
        """Create fallback image if main generation fails"""
        try:
            img = self._create_gradient_image(topic)
            img_with_text = self._add_text_overlay(img, title, topic)
            img_with_texture = self._add_noise_texture(img_with_text)
            final_img = self._add_watermark(img_with_texture)
            
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(Config.IMAGES_DIR, filename)
            final_img.save(filepath, 'PNG', quality=95)
            
            return filepath
        except Exception as e:
            logger.error(f"Fallback image creation failed: {e}")
            # Last resort - create simple colored image
            img = Image.new('RGB', (1080, 1080), color=(100, 100, 100))
            filename = f"{uuid.uuid4()}.png"
            filepath = os.path.join(Config.IMAGES_DIR, filename)
            img.save(filepath)
            return filepath
