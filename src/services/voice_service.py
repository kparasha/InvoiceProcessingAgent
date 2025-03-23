import os
from datetime import datetime
from openai import OpenAI
from src.utils.config import settings
from src.utils.logger import logger

class VoiceService:
    """Service for generating and playing voice notifications"""
    
    def __init__(self):
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not found in settings")
            return
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    def notify_finance_manager(self, message: str) -> str:
        """
        Generate and play a voice notification for the finance manager
        Returns the path to the generated audio file
        """
        try:
            if not settings.openai_api_key:
                logger.warning("Skipping voice notification - no API key")
                return None
                
            logger.info(f"Generating voice notification: {message}")
            
            # Generate speech using OpenAI's TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=message
            )
            
            # Create a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"notification_{timestamp}.mp3"
            filepath = os.path.join("static", "audio", filename)
            
            # Ensure the audio directory exists
            os.makedirs(os.path.join("static", "audio"), exist_ok=True)
            
            # Save audio to file
            response.stream_to_file(filepath)
            logger.info(f"Voice notification saved to {filepath}")
            
            # Return the relative URL path
            return f"/static/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error generating voice notification: {str(e)}")
            return None 