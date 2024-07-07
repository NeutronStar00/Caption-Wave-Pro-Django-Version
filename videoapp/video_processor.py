import whisper
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def process_video_file(video_path):
    # Your existing code, encapsulated in a function
    def transcribe_video(video_path):
        print("Starting transcription process...")
        
        # Extract audio from video
        print("Extracting audio from video...")
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile("temp_audio.wav")

        # Load Whisper model
        print("Loading Whisper model...")
        model = whisper.load_model("base")  # You can choose "tiny", "base", "small", "medium", or "large"

        # Transcribe audio
        print("Transcribing audio...")
        result = model.transcribe("temp_audio.wav", word_timestamps=True)

        # Remove temporary audio file
        os.remove("temp_audio.wav")

        # Split the transcription into segments with a maximum of 4 words
        new_segments = []
        for segment in result["segments"]:
            words = segment['words']
            for i in range(0, len(words), 1):
                chunk = words[i:i+1]
                start = chunk[0]['start']
                end = chunk[-1]['end']
                new_segments.append({'start': start, 'end': end, 'words': chunk})

        print("Transcription process completed.")
        return new_segments

    def create_caption_image(segment, current_word_index, video_width, video_height):
        words = segment['words']
        
        # Calculate font size based on video height (adjust the divisor as needed)
        font_size = int(video_height / 20)
        
        # Create an image with the full video width
        img = Image.new('RGBA', (video_width, video_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("D:\Docs\gilroy\Gilroy-Bold.ttf", font_size)
        highlight_font = ImageFont.truetype("D:\Docs\gilroy\Gilroy-Heavy.ttf", int(font_size * 1.2))
        outline_width = 2

        # Calculate maximum width for text
        max_width = video_width - 40  # 20 pixels padding on each side

        # Prepare text layout
        x = 20
        y = video_height - int(video_height / 4)
        line_height = int(font_size * 1.5)
        words_with_spaces = [word_info['word'] + ' ' for word_info in words]
        words_with_spaces[-1] = words_with_spaces[-1].strip()  # Remove space from last word

        lines = []
        current_line = []
        current_line_width = 0

        for i, word in enumerate(words_with_spaces):
            word_width = draw.textlength(word.upper(), font=font if i != current_word_index else highlight_font)
            
            if current_line_width + word_width <= max_width:
                current_line.append((i, word))
                current_line_width += word_width
            else:
                lines.append(current_line)
                current_line = [(i, word)]
                current_line_width = word_width

        if current_line:
            lines.append(current_line)

        # Adjust y position based on number of lines
        y -= (len(lines) - 1) * line_height // 2

        # Draw text
        for line in lines:
            line_width = sum(draw.textlength(word.upper(), font=font if i != current_word_index else highlight_font) for i, word in line)
            x = (video_width - line_width) // 2
            
            for i, word in line:
                if i == current_word_index:
                    word_width = draw.textlength(word.upper(), font=highlight_font)
                    
                    # Draw black outline for highlighted word
                    for xo in range(-outline_width, outline_width + 1):
                        for yo in range(-outline_width, outline_width + 1):
                            draw.text((x + xo, y + yo), word.upper(), font=highlight_font, fill=(0, 0, 0, 255))
                    
                    # Draw yellow text for highlighted word
                    draw.text((x, y), word.upper(), font=highlight_font, fill=(255, 255, 0, 255))
                else:
                    word_width = draw.textlength(word.upper(), font=font)
                    
                    # Draw black outline for regular word
                    for xo in range(-outline_width, outline_width + 1):
                        for yo in range(-outline_width, outline_width + 1):
                            draw.text((x + xo, y + yo), word.upper(), font=font, fill=(0, 0, 0, 255))
                    
                    # Draw white text for regular word
                    draw.text((x, y), word.upper(), font=font, fill=(255, 255, 255, 255))
                
                x += word_width
            
            y += line_height

        return np.array(img)

    def make_caption_frames(transcription, video_duration, video_width, video_height):
        frames = []
        for segment in transcription:
            for i, word_info in enumerate(segment['words']):
                start = word_info['start']
                end = word_info['end']
                caption_image = create_caption_image(segment, i, video_width, video_height)
                frames.append((start, end, caption_image))

        # Ensure we have frames for the entire video duration
        if frames[-1][1] < video_duration:
            last_frame = frames[-1]
            frames.append((video_duration, video_duration, last_frame[2]))

        return frames

    # Main execution
    if os.path.exists(video_path):
        # Load your video
        video = VideoFileClip(video_path)

        # Get video dimensions
        video_width, video_height = video.size

        # Generate transcription
        transcription = transcribe_video(video_path)

        # Create captions as frames
        frames = make_caption_frames(transcription, video.duration, video_width, video_height)

        # Create a list to store the caption clips
        caption_clips = []

        # Iterate through the frames to create ImageClips dynamically
        for start, end, caption in frames:
            duration = end - start
            caption_clip = ImageClip(caption).set_start(start).set_duration(duration)
            caption_clips.append(caption_clip)

        # Combine the video and caption clips
        final_video = CompositeVideoClip([video] + caption_clips)

        # Write the result to a file
        output_path = "output_video.mp4"
        final_video.write_videofile(output_path)

        return output_path
    else:
        print("Error: The specified video file does not exist.")
        return None
