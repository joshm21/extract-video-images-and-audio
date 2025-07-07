# extract_images.py
import csv
import cv2 # NOTE: This is an external library. Install with: pip install opencv-python
import os

def extract_image_crops(csv_path, videos_dir, output_images_dir):
    """
    Extracts image crops from videos based on a CSV file.

    Args:
        csv_path (str): Path to the CSV file containing annotation data.
        videos_dir (str): Directory where the video files are located.
        output_images_dir (str): Directory to save the extracted image crops.
    """
    if not os.path.exists(output_images_dir):
        os.makedirs(output_images_dir)

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

    print(f"Processing {len(annotations)} annotations for image extraction...")

    # Keep track of opened video captures to avoid reopening same video repeatedly
    video_caps = {}

    for row in annotations:
        try:
            video_filename = row['Video File Name']
            crop_time = float(row['Crop Time (s)'])
            x1, y1, x2, y2 = int(row['Crop X1']), int(row['Crop Y1']), int(row['Crop X2']), int(row['Crop Y2'])
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

        output_image_filename = f"{os.path.splitext(video_filename)[0]}_{word_id}_{clean_transcription}.png"
        output_image_path = os.path.join(output_images_dir, output_image_filename)

        if not os.path.exists(video_path):
            print(f"Warning: Video file not found for {video_filename} (ID: {word_id}). Skipping.")
            continue

        # Open video capture if not already opened
        if video_path not in video_caps:
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"Error: Could not open video file {video_filename}. Skipping.")
                    continue
                video_caps[video_path] = cap
            except Exception as e:
                print(f"Error initializing video capture for {video_filename}: {e}. Skipping.")
                continue
        else:
            cap = video_caps[video_path]

        # Set video position to the crop time
        cap.set(cv2.CAP_PROP_POS_MSEC, crop_time * 1000) # OpenCV uses milliseconds

        ret, frame = cap.read()

        if not ret:
            print(f"Warning: Could not read frame at {crop_time:.3f}s for ID {word_id} from {video_filename}. Skipping.")
            continue

        # Ensure coordinates are within frame boundaries
        h, w, _ = frame.shape
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))

        # Ensure x1 < x2 and y1 < y2 for valid crop
        if x1 >= x2 or y1 >= y2:
            print(f"Warning: Invalid crop coordinates for ID {word_id} ({x1},{y1},{x2},{y2}). Skipping crop.")
            continue

        # Crop the image
        cropped_image = frame[y1:y2, x1:x2]

        # Save the cropped image
        cv2.imwrite(output_image_path, cropped_image)
        print(f"Extracted image crop for ID {word_id} to {output_image_path}")

    # Release all video captures
    for cap in video_caps.values():
        cap.release()

    print("\nImage extraction complete.")

if __name__ == "__main__":
     # --- Configuration ---
    CSV_FILE = '/mnt/chromeos/MyFiles/Downloads/20250318_103319.mp4_annotations.csv'  # Make sure this matches your exported CSV filename
    VIDEOS_DIRECTORY = '/mnt/chromeos/MyFiles/Downloads'          # Directory where your original video files are stored
    OUTPUT_IMAGES_DIRECTORY = '/mnt/chromeos/MyFiles/Downloads' # Directory to save extracted audio

    # Create the 'videos' directory if it doesn't exist (for user's reference)
    if not os.path.exists(VIDEOS_DIRECTORY):
        print(f"Note: '{VIDEOS_DIRECTORY}' directory not found. Please place your video files here.")

    extract_image_crops(CSV_FILE, VIDEOS_DIRECTORY, OUTPUT_IMAGES_DIRECTORY)
