# extract_audio.py
import csv
import subprocess
import os
import sys # Import sys for sys.exit

def extract_audio_clips(csv_path, videos_dir, output_audio_dir):
    """
    Extracts audio clips from videos based on a CSV file.

    Args:
        csv_path (str): Path to the CSV file containing annotation data.
        videos_dir (str): Directory where the video files are located.
        output_audio_dir (str): Directory to save the extracted audio clips.
    """
    if not os.path.exists(output_audio_dir):
        os.makedirs(output_audio_dir)

    annotations = []
    try:
        with open(csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                annotations.append(row)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if not annotations:
        print("No annotations found in the CSV file.")
        return

    print(f"Processing {len(annotations)} annotations for audio extraction...")

    for row in annotations:
        try:
            video_filename = row['Video File Name']
            start_time = float(row['Start Time (s)'])
            end_time = float(row['End Time (s)'])
            transcription = row['Transcription']
            word_id = row['ID']
        except KeyError as e:
            print(f"Skipping row due to missing column: {e}. Row data: {row}")
            continue
        except ValueError as e:
            print(f"Skipping row due to invalid number format: {e}. Row data: {row}")
            continue

        video_path = os.path.join(videos_dir, video_filename)

        # Clean transcription for filename (remove special chars, limit length)
        clean_transcription = "".join([c for c in transcription if c.isalnum() or c.isspace()]).strip()
        clean_transcription = clean_transcription.replace(" ", "_")[:50] # Limit to 50 chars

        output_audio_filename = f"{os.path.splitext(video_filename)[0]}_{word_id}_{clean_transcription}.wav"
        output_audio_path = os.path.join(output_audio_dir, output_audio_filename)

        duration = end_time - start_time

        if duration <= 0:
            print(f"Skipping annotation {word_id}: Invalid duration ({duration:.3f}s).")
            continue

        if not os.path.exists(video_path):
            print(f"Warning: Video file not found for {video_filename} (ID: {word_id}). Skipping.")
            continue

        command = [
            'ffmpeg',
            '-y',                     # Automatically overwrite output files
            '-i', video_path,         # Input file FIRST
            '-ss', str(start_time),   # Precise seek to start time (after -i)
            '-to', str(end_time),     # Precise end time
            '-vn',                    # No video output
            '-q:a', '0',              # High quality audio encoding (MP3 specific)
            '-map', '0:a:0',          # Map the first audio stream (or just 'a' for all audio)
            output_audio_path
        ]

        try:
            # Using stdout=subprocess.DEVNULL and stderr=subprocess.DEVNULL to suppress ffmpeg output
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Extracted audio for ID {word_id} to {output_audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio for ID {word_id} from {video_filename}: {e}")
            # print(f"FFmpeg stderr: {e.stderr.decode()}") # Uncomment for detailed ffmpeg errors
        except FileNotFoundError:
            print("Error: ffmpeg command not found. Please ensure ffmpeg is installed and in your system's PATH.")
            sys.exit(1) # Exit if ffmpeg is not found, as it's a critical dependency

    print("\nAudio extraction complete.")

if __name__ == "__main__":
    # --- Configuration ---
    CSV_FILE = '/mnt/chromeos/MyFiles/Downloads/20250318_103319.mp4_annotations.csv'  # Make sure this matches your exported CSV filename
    VIDEOS_DIRECTORY = '/mnt/chromeos/MyFiles/Downloads'          # Directory where your original video files are stored
    OUTPUT_AUDIO_DIRECTORY = '/mnt/chromeos/MyFiles/Downloads' # Directory to save extracted audio

    # Create the 'videos' directory if it doesn't exist (for user's reference)
    if not os.path.exists(VIDEOS_DIRECTORY):
        print(f"Note: '{VIDEOS_DIRECTORY}' directory not found. Please place your video files here.")

    extract_audio_clips(CSV_FILE, VIDEOS_DIRECTORY, OUTPUT_AUDIO_DIRECTORY)
