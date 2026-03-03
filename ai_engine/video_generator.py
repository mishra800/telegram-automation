"""
Video Generator Module
Generates 15-30 second vertical videos (1080x1920) for Telegram
"""

import os
import random
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

# Try to import MoviePy
try:
    from moviepy.editor import (
        VideoClip, ImageClip, TextClip, CompositeVideoClip,
        concatenate_videoclips, AudioFileClip
    )
    from moviepy.video.fx import fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("MoviePy not available, video generation disabled")

class VideoGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.slide_duration = 3.5  # seconds per slide
        self.fade_duration = 0.5  # fade in/out duration
        
        # Video directory
        self.videos_dir = os.path.join(Config.BASE_DIR, 'videos')
        os.makedirs(self.videos_dir, exist_ok=True)
        
        # Gradient palettes (same as image generator)
        self.gradient_palettes = {
            'motivational': [
                [(255, 179, 71), (255, 107, 107)],
                [(255, 94, 77), (251, 194, 235)],
                [(254, 140, 0), (248, 54, 0)],
                [(255, 200, 124), (252, 251, 121)],
                [(243, 144, 79), (59, 67, 113)]
            ],
            'tech_news': [
                [(67, 97, 238), (76, 201, 240)],
                [(13, 27, 42), (27, 43, 52)],
                [(0, 180, 219), (0, 131, 176)],
                [(30, 60, 114), (42, 82, 152)],
                [(72, 52, 212), (130, 119, 255)]
            ],
            'ai_updates': [
                [(138, 43, 226), (75, 0, 130)],
                [(159, 18, 255), (231, 74, 59)],
                [(102, 126, 234), (118, 75, 162)],
                [(79, 172, 254), (0, 242, 254)],
                [(195, 55, 100), (29, 38, 113)]
            ],
            'data_science': [
                [(34, 193, 195), (253, 187, 45)],
                [(0, 198, 255), (0, 114, 255)],
                [(19, 84, 122), (128, 208, 199)],
                [(52, 143, 80), (86, 180, 211)],
                [(255, 75, 145), (255, 200, 55)]
            ],
            'productivity': [
                [(0, 180, 216), (0, 119, 182)],
                [(108, 92, 231), (192, 108, 132)],
                [(76, 161, 175), (196, 224, 229)],
                [(30, 150, 252), (142, 209, 252)],
                [(99, 179, 237), (6, 190, 182)]
            ]
        }
    
    def generate_video(self, topic, content_text):
        """Generate video from content text"""
        if not MOVIEPY_AVAILABLE:
            logger.error("MoviePy not available, cannot generate video")
            return None
        
        try:
            logger.info(f"Generating video for topic: {topic}")
            
            # Split content into slides
            slides = self._split_content_into_slides(content_text)
            logger.info(f"Created {len(slides)} slides")
            
            # Generate video clips for each slide
            video_clips = []
            
            for i, slide_text in enumerate(slides):
                clip = self._create_slide_clip(slide_text, topic, i)
                video_clips.append(clip)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Add background music if available (optional)
            final_video = self._add_background_music(final_video)
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}.mp4"
            filepath = os.path.join(self.videos_dir, filename)
            
            # Export video optimized for Telegram
            logger.info("Exporting video...")
            final_video.write_videofile(
                filepath,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                bitrate='2000k',
                threads=4,
                logger=None  # Suppress MoviePy output
            )
            
            # Clean up
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            logger.info(f"Video saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating video: {e}", exc_info=True)
            return None
    
    def _split_content_into_slides(self, content_text):
        """Split content into slides (3-5 slides)"""
        lines = content_text.strip().split('\n')
        
        # Filter out empty lines
        lines = [line.strip() for line in lines if line.strip()]
        
        slides = []
        current_slide = []
        
        for line in lines:
            # Title or heading (emoji at start or all caps)
            if line.startswith(('🌟', '🚀', '💡', '⚡', '🎯', '📊', '🤖', '💰')) or line.isupper():
                if current_slide:
                    slides.append('\n'.join(current_slide))
                    current_slide = []
                current_slide.append(line)
            
            # Bullet points
            elif line.startswith(('•', '-', '*')):
                current_slide.append(line)
                
                # Create new slide after 3-4 bullet points
                if len([l for l in current_slide if l.startswith(('•', '-', '*'))]) >= 4:
                    slides.append('\n'.join(current_slide))
                    current_slide = []
            
            # Regular text
            else:
                current_slide.append(line)
        
        # Add remaining content
        if current_slide:
            slides.append('\n'.join(current_slide))
        
        # Limit to 3-5 slides for 15-30 second video
        if len(slides) > 5:
            slides = slides[:5]
        elif len(slides) < 3:
            # If too few slides, split longer ones
            while len(slides) < 3 and any(len(s.split('\n')) > 3 for s in slides):
                for i, slide in enumerate(slides):
                    lines = slide.split('\n')
                    if len(lines) > 3:
                        mid = len(lines) // 2
                        slides[i] = '\n'.join(lines[:mid])
                        slides.insert(i + 1, '\n'.join(lines[mid:]))
                        break
        
        return slides
    
    def _create_slide_clip(self, text, topic, slide_index):
        """Create a video clip for a single slide"""
        # Create background
        background = self._create_gradient_background(topic)
        
        # Create background clip
        bg_clip = ImageClip(background).set_duration(self.slide_duration)
        
        # Create text overlay
        text_clip = self._create_text_overlay(text, slide_index)
        
        # Composite background and text
        composite = CompositeVideoClip([bg_clip, text_clip])
        
        # Add fade in/out
        composite = composite.fx(fadein, self.fade_duration)
        composite = composite.fx(fadeout, self.fade_duration)
        
        return composite
    
    def _create_gradient_background(self, topic):
        """Create gradient background image"""
        # Select random palette
        palettes = self.gradient_palettes.get(topic, self.gradient_palettes['motivational'])
        color1, color2 = random.choice(palettes)
        
        # Create vertical gradient
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        for y in range(self.height):
            progress = y / self.height
            r = int(color1[0] + (color2[0] - color1[0]) * progress)
            g = int(color1[1] + (color2[1] - color1[1]) * progress)
            b = int(color1[2] + (color2[2] - color1[2]) * progress)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        # Add subtle noise
        noise = np.random.randint(0, 15, (self.height, self.width, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise, mode='RGB')
        img = Image.blend(img, noise_img, alpha=0.03)
        
        # Convert to numpy array for MoviePy
        return np.array(img)
    
    def _create_text_overlay(self, text, slide_index):
        """Create animated text overlay"""
        # Clean text
        text = text.strip()
        
        # Determine font size based on text length
        text_length = len(text)
        if text_length < 50:
            fontsize = 80
        elif text_length < 100:
            fontsize = 65
        elif text_length < 150:
            fontsize = 55
        else:
            fontsize = 45
        
        # Create text clip with word wrap
        try:
            text_clip = TextClip(
                text,
                fontsize=fontsize,
                color='white',
                font='Arial-Bold',
                size=(self.width - 100, None),  # Width with padding
                method='caption',
                align='center'
            )
        except:
            # Fallback if Arial-Bold not available
            try:
                text_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    color='white',
                    font='Arial',
                    size=(self.width - 100, None),
                    method='caption',
                    align='center'
                )
            except:
                # Last resort fallback
                text_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    color='white',
                    size=(self.width - 100, None),
                    method='caption',
                    align='center'
                )
        
        # Position text in center
        text_clip = text_clip.set_position('center')
        text_clip = text_clip.set_duration(self.slide_duration)
        
        # Add shadow effect by creating a black copy slightly offset
        try:
            shadow_clip = TextClip(
                text,
                fontsize=fontsize,
                color='black',
                font='Arial-Bold',
                size=(self.width - 100, None),
                method='caption',
                align='center'
            )
            shadow_clip = shadow_clip.set_position(('center', 'center'))
            shadow_clip = shadow_clip.set_duration(self.slide_duration)
            shadow_clip = shadow_clip.set_opacity(0.5)
            
            # Composite shadow and text
            text_with_shadow = CompositeVideoClip([shadow_clip, text_clip])
            return text_with_shadow
        except:
            # If shadow fails, return text without shadow
            return text_clip
    
    def _add_background_music(self, video_clip):
        """Add background music if available (optional)"""
        try:
            # Look for background music file
            music_file = os.path.join(Config.BASE_DIR, 'assets', 'background_music.mp3')
            
            if os.path.exists(music_file):
                audio = AudioFileClip(music_file)
                
                # Loop audio if video is longer
                if audio.duration < video_clip.duration:
                    audio = audio.loop(duration=video_clip.duration)
                else:
                    audio = audio.subclip(0, video_clip.duration)
                
                # Reduce volume to 20%
                audio = audio.volumex(0.2)
                
                # Add audio to video
                video_clip = video_clip.set_audio(audio)
                logger.info("Background music added")
            else:
                logger.info("No background music file found, skipping")
        
        except Exception as e:
            logger.warning(f"Could not add background music: {e}")
        
        return video_clip
    
    def is_available(self):
        """Check if video generation is available"""
        return MOVIEPY_AVAILABLE

def test_video_generator():
    """Test the video generator"""
    if not MOVIEPY_AVAILABLE:
        print("❌ MoviePy not available. Install with: pip install moviepy")
        return
    
    print("=" * 60)
    print("VIDEO GENERATOR TEST")
    print("=" * 60)
    
    generator = VideoGenerator()
    
    print(f"\n✅ Video generator initialized")
    print(f"   Resolution: {generator.width}x{generator.height}")
    print(f"   FPS: {generator.fps}")
    print(f"   Slide duration: {generator.slide_duration}s")
    print(f"   Videos directory: {generator.videos_dir}")
    
    # Test content
    test_content = """🌟 Success Starts Today

• Set clear goals before you begin
• Focus on progress, not perfection
• Celebrate small wins daily
• Stay consistent with your habits
• Believe in your potential

Take action today! What's your first step?

#Motivation #Success #Growth"""
    
    print("\n🎬 Generating test video...")
    print(f"   Content length: {len(test_content)} characters")
    
    video_path = generator.generate_video('motivational', test_content)
    
    if video_path:
        print(f"\n✅ Video generated successfully!")
        print(f"   Path: {video_path}")
        
        # Check file size
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        print(f"   Size: {file_size:.2f} MB")
        
        print("\n📊 Video Details:")
        print(f"   Format: MP4 (H.264)")
        print(f"   Resolution: 1080x1920 (vertical)")
        print(f"   Optimized for: Telegram")
    else:
        print("\n❌ Video generation failed")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_video_generator()
