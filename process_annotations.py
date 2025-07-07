# process_annotations.py
import argparse
import os
import glob
import sys
from datetime import datetime

# Attempt to import the extraction functions from the other scripts
try:
    from extract_audio import extract_audio_clips
    from extract_images import extract_image_crops
except ImportError:
    print("Error: Make sure 'extract_audio.py' and 'extract_images.py' are in the same directory as this script.")
    print("Please check your file paths and dependencies.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Process video annotations: extract audio clips and image crops based on CSVs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows default values in help
    )

    parser.add_argument(
        "-i", "--input-dir",
        default=".",
        help="Directory containing both original video files and annotation CSV files."
    )
    parser.add_argument(
        "-o", "--output-folder-name", # Renamed for clarity: this is the folder name within input-dir
        default="output",
        help="Name of the output folder to be created inside the input directory."
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        default=True,
        help="Enable audio extraction."
    )
    parser.add_argument(
        "--no-audio",
        action="store_false",
        dest="audio",
        help="Disable audio extraction."
    )
    parser.add_argument(
        "--images",
        action="store_true",
        default=True,
        help="Enable image extraction."
    )
    parser.add_argument(
        "--no-images",
        action="store_false",
        dest="images",
        help="Disable image extraction."
    )
    parser.add_argument(
        "--video-extensions",
        default=".mp4,.mov,.avi,.mkv,.webm",
        help="Comma-separated list of video file extensions to look for."
    )

    args = parser.parse_args()

    # Determine the absolute path for the input directory
    abs_input_dir = os.path.abspath(args.input_dir)

    # Determine the absolute path for the base output directory
    abs_output_base_dir = os.path.join(abs_input_dir, args.output_folder_name)
    os.makedirs(abs_output_base_dir, exist_ok=True)

    video_extensions = tuple(ext.strip().lower() for ext in args.video_extensions.split(','))

    print(f"Process Annotations Script Started (Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"  Input directory: '{abs_input_dir}'")
    print(f"  Base output directory: '{abs_output_base_dir}'")
    print(f"  Audio extraction: {'Enabled' if args.audio else 'Disabled'}")
    print(f"  Image extraction: {'Enabled' if args.images else 'Disabled'}")
    print(f"  Accepted video extensions: {', '.join(video_extensions)}")
    print("-" * 60)

    processed_count = 0
    skipped_count = 0

    # Find all CSV files that match the pattern *_annotations.csv within the input directory
    csv_pattern = os.path.join(abs_input_dir, "*_annotations.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        print(f"No annotation CSV files found matching '{csv_pattern}'. Nothing to process.")
        return

    for csv_path in sorted(csv_files): # Sort for consistent processing order
        csv_basename = os.path.basename(csv_path)

        # Derive the full video filename (e.g., 'my_video.mp4') from the CSV filename
        video_filename_from_csv = csv_basename.replace("_annotations.csv", "")

        found_video_path = None
        # Construct the full path to the potential video file within the input directory
        potential_video_path = os.path.join(abs_input_dir, video_filename_from_csv)

        # Check if the potential video file exists AND if its extension is in our accepted list
        if os.path.exists(potential_video_path) and \
           os.path.splitext(potential_video_path)[1].lower() in video_extensions:
            found_video_path = potential_video_path

        if found_video_path:
            print(f"\n--- Processing CSV: '{csv_basename}' (Matched Video: '{os.path.basename(found_video_path)}') ---")

            # Create a unique output subdirectory for this video's extracts
            # e.g., 'output/my_video/' (removes video extension for cleaner folder name)
            video_output_folder_name = os.path.splitext(video_filename_from_csv)[0]
            current_video_output_dir = os.path.join(abs_output_base_dir, video_output_folder_name)
            os.makedirs(current_video_output_dir, exist_ok=True)

            # Call audio extraction script
            if args.audio:
                audio_output_dir = os.path.join(current_video_output_dir, "audio")
                print(f"  > Starting audio extraction to: '{audio_output_dir}'")
                # Pass the input directory for videos, as extract_audio_clips expects it
                extract_audio_clips(csv_path, abs_input_dir, audio_output_dir)
            else:
                print("  > Audio extraction skipped for this video.")

            # Call image extraction script
            if args.images:
                images_output_dir = os.path.join(current_video_output_dir, "images")
                print(f"  > Starting image extraction to: '{images_output_dir}'")
                # Pass the input directory for videos, as extract_image_crops expects it
                extract_image_crops(csv_path, abs_input_dir, images_output_dir)
            else:
                print("  > Image extraction skipped for this video.")

            processed_count += 1
        else:
            print(f"\n--- Skipping '{csv_basename}': No matching video file found for '{video_filename_from_csv}' in '{abs_input_dir}' with accepted extensions. ---")
            skipped_count += 1

    print("\n" + "=" * 60)
    print(f"Processing Summary: Processed {processed_count} video(s), skipped {skipped_count} CSV(s).\n")
    print("=" * 60)

if __name__ == "__main__":
    main()
