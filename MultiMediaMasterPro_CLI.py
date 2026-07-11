import os
import csv
import time
import subprocess
from datetime import datetime
import logging
import sys

import shutil

def setup_logging():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(application_path, "app_debug.log")
    
    logging.basicConfig(
        filename=log_file,
        filemode='w',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Application started")
    logging.info(f"Log file created at: {log_file}")

def get_config_dir():
    """
    Return a per-user, always-writable directory for storing app settings
    (e.g. the saved screen-recording output path). Using a fixed writable
    location avoids 'Permission denied' errors that happen when the app runs
    from a read-only folder such as Program Files.
    """
    if os.name == 'nt':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    else:
        base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')

    config_dir = os.path.join(base, 'MultiMediaMasterPro')
    try:
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    except Exception as e:
        logging.error(f"Could not create config directory {config_dir}: {e}")
        # Fall back to the user's home directory, then the current directory
        for fallback in (os.path.expanduser('~'), os.getcwd()):
            try:
                os.makedirs(fallback, exist_ok=True)
                return fallback
            except Exception:
                continue
        return os.getcwd()


def get_output_dir_file():
    """Full path to the file that stores the saved screen-recording output path."""
    return os.path.join(get_config_dir(), 'output_dir.txt')


def get_ffmpeg_path():
    """
    Locate ffmpeg.exe in the following order:
    1. _internal folder (PyInstaller one-dir mode)
    2. Current directory (where the script/exe is located)
    3. System PATH
    """
    # Check _internal directory (PyInstaller)
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Typical PyInstaller internal structure or local dev
    internal_path = os.path.join(base_path, '_internal', 'ffmpeg.exe') # Check nested _internal
    if os.path.exists(internal_path):
        return internal_path
    
    internal_root = os.path.join(base_path, 'ffmpeg.exe') # Check root of bundled app
    if os.path.exists(internal_root):
        return internal_root

    # Check current working directory
    cwd_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
    if os.path.exists(cwd_path):
        return cwd_path
        
    # Check system PATH
    system_path = shutil.which("ffmpeg")
    if system_path:
        return system_path
        
    return "ffmpeg.exe" # Fallback to default command

# Global ffmpeg command
FFMPEG_CMD = get_ffmpeg_path()

if os.path.exists(FFMPEG_CMD) or shutil.which("ffmpeg"):
    logging.info(f"FFmpeg found at: {FFMPEG_CMD}")
else:
    logging.critical("FFmpeg not found in _internal, current directory, or PATH.")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

setup_logging()


def get_file_size(file_path):
    try:
        file_size = os.path.getsize(file_path) // 1024  # Convert bytes to kilobytes
        return file_size
    except Exception as e:
        logging.error(f"Error getting file size for {file_path}: {e}")
        return False


def compress_videos(input_path, output_path, given_extension=None, compression_level=2):
    global video_extensions
    # Flag to check any error
    any_error = False
    logging.info(f"Starting directory video compression. Input: {input_path}, Output: {output_path}, Level: {compression_level}")
    
    # Set CRF values and bitrates based on compression level
    if compression_level == 1:  # Low bitrate compression (larger file)
        crf_value = "20"
        audio_bitrate = "128k"
    elif compression_level == 3:  # High bitrate compression (smaller file)
        crf_value = "30"
        audio_bitrate = "64k"
    else:  # Medium bitrate compression (default)
        crf_value = "25"
        audio_bitrate = "96k"
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # List all files in the input directory
    files = os.listdir(input_path)

    # Filter video files 
    video_files = [file for file in files if file.lower().endswith(video_extensions)]

    # Open CSV file for writing
    csv_file_path = os.path.join(output_path, 'compression_data.csv')
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            ['File', 'Actual File Size (KB)', 'Compressed File Size (KB)', 'Remaining Size (%)', 'Size Reduction (%)'])

        # Compress each video file
        for video_file in video_files:
            input_file_path = os.path.join(input_path, video_file)
            if given_extension is None:
                output_file_path = os.path.join(output_path, video_file)
            else:
                filename, _ = os.path.splitext(video_file)
                output_file_path = os.path.join(output_path, (f"{filename}.{given_extension}"))
                            
            # Get the actual file size before compression
            actual_size = get_file_size(input_file_path)
            if not actual_size:
                print("File couldn't be found, Check permissions")
                logging.error(f"File not found or inaccessible: {input_file_path}")
                any_error = True
                break
            
            # Run ffmpeg command to compress the video with specified quality level          
            try:
                subprocess.run([
                    FFMPEG_CMD, "-i", input_file_path,
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", crf_value,
                    "-c:a", "aac",
                    "-b:a", audio_bitrate,
                    "-movflags", "+faststart",
                    "-y",  # Overwrite output file if it exists
                    output_file_path
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(" Video compression failed.")
                logging.error(f"Video compression failed for {input_file_path}: {e}")
                return
            except Exception as e:
                logging.error(f"Unexpected error during video compression for {input_file_path}: {e}", exc_info=True)
                return
            
            # Get the compressed file size after compression
            compressed_size = get_file_size(output_file_path)

            # Calculate remaining size percentage and size reduction
            if compressed_size and actual_size:
                remaining_size_percentage = (compressed_size / actual_size) * 100
                size_reduction = ((actual_size - compressed_size) / actual_size) * 100
            else:
                remaining_size_percentage = 0
                size_reduction = 0

            # Write data to CSV file
            csv_writer.writerow([video_file, actual_size, compressed_size, f"{remaining_size_percentage:.1f}", f"{size_reduction:.1f}"])
            print(f" Compression successful: {video_file} - Size reduction: {size_reduction:.1f}%")
            logging.info(f"Compressed {video_file}: {actual_size}KB -> {compressed_size}KB ({size_reduction:.1f}% reduction)")

    if any_error:
        return
    print(f" All videos compressed and exported to {output_path}")
    print(f" Compression data written to {csv_file_path}")
    
    base_dir, last_dir = os.path.split(output_path)
    if str(last_dir).upper() != "DESKTOP":
        os.system(f"explorer {output_path}")
        
        
def compress_video():
    logging.info("Starting single video compression")
    # Prompt the user for the input video file
    input_path = input(" Enter the path to the input video file: ").strip()
    
    # Remove quotes from the input path if present
    input_path = input_path.strip('"')
    
    # Check if the input file exists
    if not os.path.exists(input_path):
        print(" The specified input file does not exist.")
        logging.warning(f"Input file does not exist: {input_path}")
        return

    # Get the file name and directory of the input video
    input_dir, input_name = os.path.split(input_path)
    input_name, input_extension = os.path.splitext(input_name)
    
    # Choose compression level
    print("\n Select compression level:")
    print(" [1] Low bitrate compression (CRF 20, larger file size)")
    print(" [2] Medium bitrate compression (CRF 25, balanced file size)")
    print(" [3] High bitrate compression (CRF 30, smaller file size)")
    
    try:
        compression_choice = int(input(" Choose compression level (1-3): ").strip())
        if compression_choice not in [1, 2, 3]:
             raise ValueError
    except ValueError:
        print(" Invalid input! Using medium bitrate compression by default.")
        logging.warning("Invalid compression level input. Defaulting to medium.")
        compression_choice = 2
    
    # Set CRF values and bitrates based on compression level
    if compression_choice == 1:  # Low bitrate compression (larger file)
        crf_value = "20"
        audio_bitrate = "128k"
        compression_suffix = "_low_bitrate"
    elif compression_choice == 3:  # High bitrate compression (smaller file)
        crf_value = "30"
        audio_bitrate = "64k"
        compression_suffix = "_high_bitrate"
    else:  # Medium bitrate compression (default)
        crf_value = "25"
        audio_bitrate = "96k"
        compression_suffix = "_medium_bitrate"
    
    choice = input(" Do you want to change the extension (Y/N): ").upper()
    
    if choice == "Y":
        given_extension = input(" Enter the extension without dot (.): ").lower().strip().strip(".")
        if given_extension not in video_extensions:
            print(" FFMPEG can't handle this video format!\n Try any other extensions.")
            logging.warning(f"Invalid extension provided: {given_extension}")
            return
        output_name = f"{input_name}{compression_suffix}.{given_extension}"
    else:
        # Fix the extra dot bug by removing the leading dot from input_extension
        extension_without_dot = input_extension.lstrip('.')
        output_name = f"{input_name}{compression_suffix}.{extension_without_dot}"

    output_path = os.path.join(input_dir, output_name)
    
    # Get original file size before compression
    original_size = get_file_size(input_path)
    if not original_size:
        print(" Could not determine original file size.")
        logging.error(f"Could not determine original file size for {input_path}")
        return
    
    start_time = time.time()
    
    # Compress the video using FFmpeg with selected compression level
    try:
        subprocess.run([
            FFMPEG_CMD, "-i", input_path, 
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", crf_value,
            "-c:a", "aac", 
            "-b:a", audio_bitrate,
            "-movflags", "+faststart",
            "-y",  # Overwrite output file if it exists
            output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(" Video compression failed.")
        logging.error(f"Video compression failed for {input_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error during video compression for {input_path}: {e}", exc_info=True)
        return
    
    # Get compressed file size and calculate remaining size percentage
    compressed_size = get_file_size(output_path)
    if compressed_size:
        remaining_size_percentage = (compressed_size / original_size) * 100
        size_reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"\n Video compression successful with {['low', 'medium', 'high'][compression_choice-1]} compression level.")
        print(" Output file:", output_path)
        print(f" Original file size: {original_size} KB")
        print(f" Compressed file size: {compressed_size} KB")
        print(f" Remaining size: {remaining_size_percentage:.1f}%")
        print(f" Size reduction: {size_reduction:.1f}%")
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
    else:
        print(f"\n Video compression successful with {['low', 'medium', 'high'][compression_choice-1]} compression level.")
        print(" Output file:", output_path)
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds") 
    base_dir, last_dir = os.path.split(input_dir)
    if str(last_dir).upper() != "DESKTOP":
        os.system(f"explorer {input_dir}")

    
def record_screen():
    logging.info("Starting screen recording setup")
    # Get current date and time
    current_datetime = datetime.now()
    year = str(current_datetime.year)
    month = str(current_datetime.month).zfill(2)
    day = str(current_datetime.day).zfill(2)
    hour = str(current_datetime.hour).zfill(2)
    minute = str(current_datetime.minute).zfill(2)
    second = str(current_datetime.second).zfill(2)

    output_directory = None
    output_dir_file = get_output_dir_file()
    if os.path.exists(output_dir_file):
        with open(output_dir_file, 'r') as file:
            output_directory = file.read().strip()
    else:
        print(" Output path is not set! Use option [6] to save it first.")
        return
    if output_directory is None or output_directory == '':
        print(" Output path is not given!")
        return
        
    output_filename = f"{year}-{month}-{day}-{hour}-{minute}-{second}.mp4"
    output_path = os.path.join(output_directory, output_filename)

    # Run ffmpeg command to record screen
    try:
        # Use subprocess.run instead of os.system for better control and consistency
        subprocess.run(f'"{FFMPEG_CMD}" -f gdigrab -i desktop -c:v libx264 -crf 25 -pix_fmt yuv420p "{output_path}"', shell=True, check=True)
    except subprocess.CalledProcessError:
        pass
    print(" Screen Recording Ended!")
    
    
def extract_audio():
    logging.info("Starting audio extraction")
    # Prompt for input path (file or directory)
    input_path = input(" Enter the path to the input file or directory: ").strip().strip('"')

    if not os.path.exists(input_path):
        print(" The specified path does not exist.")
        return

    # Ask for Single or Directory
    mode = input(" Single File or Directory of Videos (s/d): ").lower().strip()

    if mode == 's':
        if not os.path.isfile(input_path):
            print(" Path is not a file!")
            return
            
        # Get the file name and directory of the input video
        input_dir, input_name = os.path.split(input_path)
        input_name, _ = os.path.splitext(input_name)
        
        output_name = f"{input_name}.mp3"
        output_path = os.path.join(input_dir, output_name)
        
        start_time = time.time()
        try:
            subprocess.run([FFMPEG_CMD, "-i", input_path, "-q:a", "0", "-map", "a", "-y", output_path], check=True)
            print(f"\n Audio Extracted successfully. Output file: {output_path}")
        except subprocess.CalledProcessError as e:
            print(" Audio Extraction failed.")
            logging.error(f"Audio extraction failed for {input_path}: {e}")
            return
        except Exception as e:
            logging.error(f"Unexpected error during audio extraction for {input_path}: {e}", exc_info=True)
            return
        
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds")

    elif mode == 'd':
        if not os.path.isdir(input_path):
            print(" Path is not a directory!")
            return

        output_directory = input_path + "_audio"
        os.makedirs(output_directory, exist_ok=True)
        
        # Access global video extensions if needed, assuming they're available
        global video_extensions
        files = [f for f in os.listdir(input_path) if f.lower().endswith(video_extensions)]
        
        if not files:
            print(" No video files found in the directory.")
            return
            
        start_time = time.time()
        print(f" Found {len(files)} video files. Starting extraction...")
        
        for video_file in files:
            input_file_path = os.path.join(input_path, video_file)
            filename, _ = os.path.splitext(video_file)
            output_file_path = os.path.join(output_directory, f"{filename}.mp3")
            
            try:
                subprocess.run([FFMPEG_CMD, "-i", input_file_path, "-q:a", "0", "-map", "a", "-y", output_file_path], check=True)
                print(f" Extracted: {video_file}")
            except subprocess.CalledProcessError as e:
                print(f" Failed to extract: {video_file}")
                logging.error(f"Failed to extract audio from {video_file}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error extracting audio from {video_file}: {e}", exc_info=True)
                
        print(f" \n All operations completed. Output directory: {output_directory}")
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
        
        if os.name == 'nt':
             os.system(f"explorer {output_directory}")

    else:
        print(" Invalid choice!")

def compress_image():
    logging.info("Starting single image compression")
    # Prompt the user for the input image file
    input_path = input(" Enter the path to the input image file: ").strip()
    
    # Remove quotes from the input path if present
    input_path = input_path.strip('"')
    
    # Check if the input file exists
    if not os.path.exists(input_path):
        print(" The specified input file does not exist.")
        logging.warning(f"Input file does not exist: {input_path}")
        return

    # Get the file name and directory of the input image
    input_dir, input_name = os.path.split(input_path)
    input_name, input_extension = os.path.splitext(input_name)
    
    # Choose compression level
    print("\n Select compression level:")
    print(" [1] Low compression (Quality 95, larger file size)")
    print(" [2] Medium compression (Quality 85, balanced file size)")
    print(" [3] High compression (Quality 70, smaller file size)")
    
    try:
        compression_choice = int(input(" Choose compression level (1-3): ").strip())
        if compression_choice not in [1, 2, 3]:
             raise ValueError
    except ValueError:
        print(" Invalid input! Using medium compression by default.")
        logging.warning("Invalid compression level input. Defaulting to medium.")
        compression_choice = 2
    
    # Set quality values based on compression level
    if compression_choice == 1:  # Low compression (higher quality setting)
        quality = "95"
        compression_suffix = "_q95_compressed"
    elif compression_choice == 3:  # High compression (lower quality setting)
        quality = "70"
        compression_suffix = "_q70_compressed"
    else:  # Medium compression (default quality setting)
        quality = "85"
        compression_suffix = "_q85_compressed"
    
    choice = input(" Do you want to change the extension (Y/N): ").upper()
    
    if choice == "Y":
        given_extension = input(" Enter the extension without dot (.): ").lower().strip().strip(".")
        if given_extension not in image_extensions:
            print(" FFMPEG can't handle this image format!\n Try any other extensions.")
            logging.warning(f"Invalid extension provided: {given_extension}")
            return
        output_name = f"{input_name}{compression_suffix}.{given_extension}"
    else:
        # Fix the extra dot bug by removing the leading dot from input_extension
        extension_without_dot = input_extension.lstrip('.')
        output_name = f"{input_name}{compression_suffix}.{extension_without_dot}"

    output_path = os.path.join(input_dir, output_name)
    
    # Get original file size before compression
    original_size = get_file_size(input_path)
    if not original_size:
        print(" Could not determine original file size.")
        logging.error(f"Could not determine original file size for {input_path}")
        return
    
    start_time = time.time()
    
    # Compress the image using FFmpeg with selected compression level
    try:
        subprocess.run([
            FFMPEG_CMD, "-i", input_path, 
            "-q:v", quality,
            "-y",  # Overwrite output file if it exists
            output_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(" Image compression failed.")
        logging.error(f"Image compression failed for {input_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error during image compression for {input_path}: {e}", exc_info=True)
        return
    
    # Get compressed file size and calculate remaining size percentage
    compressed_size = get_file_size(output_path)
    if compressed_size:
        remaining_size_percentage = (compressed_size / original_size) * 100
        size_reduction = ((original_size - compressed_size) / original_size) * 100
        
        print(f"\n Image compression successful with {['low', 'medium', 'high'][compression_choice-1]} compression level.")
        print(" Output file:", output_path)
        print(f" Original file size: {original_size} KB")
        print(f" Compressed file size: {compressed_size} KB")
        print(f" Remaining size: {remaining_size_percentage:.1f}%")
        print(f" Size reduction: {size_reduction:.1f}%")
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
    else:
        print(f"\n Image compression successful with {['low', 'medium', 'high'][compression_choice-1]} compression level.")
        print(" Output file:", output_path)
        print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
    
    base_dir, last_dir = os.path.split(input_dir)
    if str(last_dir).upper() != "DESKTOP":
        os.system(f"explorer {input_dir}")


def compress_images(input_path, output_path, given_extension=None, compression_level=2):
    global image_extensions
    # Flag to check any error
    any_error = False
    logging.info(f"Starting directory image compression. Input: {input_path}, Output: {output_path}, Level: {compression_level}")
    
    # Set quality values based on compression level
    if compression_level == 1:  # Low compression (higher quality setting)
        quality = "95"
    elif compression_level == 3:  # High compression (lower quality setting)
        quality = "70"
    else:  # Medium compression (default quality setting)
        quality = "85"
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # List all files in the input directory
    files = os.listdir(input_path)

    # Filter image files 
    image_files = [file for file in files if file.lower().endswith(image_extensions)]

    # Open CSV file for writing
    csv_file_path = os.path.join(output_path, 'compression_data.csv')
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(
            ['File', 'Actual File Size (KB)', 'Compressed File Size (KB)', 'Remaining Size (%)', 'Size Reduction (%)'])

        # Compress each image file
        for image_file in image_files:
            input_file_path = os.path.join(input_path, image_file)
            if given_extension is None:
                output_file_path = os.path.join(output_path, image_file)
            else:
                filename, _ = os.path.splitext(image_file)
                output_file_path = os.path.join(output_path, (f"{filename}.{given_extension}"))
                            
            # Get the actual file size before compression
            actual_size = get_file_size(input_file_path)
            if not actual_size:
                print("File couldn't be found, Check permissions")
                logging.error(f"File not found or inaccessible: {input_file_path}")
                any_error = True
                break
            
            # Run ffmpeg command to compress the image with specified quality level          
            try:
                subprocess.run([
                    FFMPEG_CMD, "-i", input_file_path,
                    "-q:v", quality,
                    "-y",  # Overwrite output file if it exists
                    output_file_path
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(" Image compression failed.")
                logging.error(f"Image compression failed for {input_file_path}: {e}")
                return
            except Exception as e:
                logging.error(f"Unexpected error during image compression for {input_file_path}: {e}", exc_info=True)
                return
            
            # Get the compressed file size after compression
            compressed_size = get_file_size(output_file_path)

            # Calculate remaining size percentage and size reduction
            if compressed_size and actual_size:
                remaining_size_percentage = (compressed_size / actual_size) * 100
                size_reduction = ((actual_size - compressed_size) / actual_size) * 100
            else:
                remaining_size_percentage = 0
                size_reduction = 0

            # Write data to CSV file
            csv_writer.writerow([image_file, actual_size, compressed_size, f"{remaining_size_percentage:.1f}", f"{size_reduction:.1f}"])
            print(f" Compression successful: {image_file} - Size reduction: {size_reduction:.1f}%")
            logging.info(f"Compressed {image_file}: {actual_size}KB -> {compressed_size}KB ({size_reduction:.1f}% reduction)")

    if any_error:
        return
    print(f" All images compressed and exported to {output_path}")
    print(f" Compression data written to {csv_file_path}")
    
    base_dir, last_dir = os.path.split(output_path)
    if str(last_dir).upper() != "DESKTOP":
        os.system(f"explorer {output_path}")


def image_converter(input_path, extension, single=True):
    logging.info(f"Starting image conversion. Input: {input_path}, Extension: {extension}")
    
    # Get the file name and directory of the input video
    input_dir, input_name = os.path.split(input_path)
    input_name, input_extension = os.path.splitext(input_name)

    
    output_name = f"{input_name}.{extension}"
    if single:
        output_path = os.path.join(input_dir, output_name)
    else:
        output_dir = os.path.join((input_dir + f"_{extension}"))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_name)
         
    try:
        subprocess.run([FFMPEG_CMD, "-i", input_path, output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(" Conversion failed.")
        logging.error(f"Conversion failed for {input_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error during conversion for {input_path}: {e}", exc_info=True)
        return
    
    print("\n Conversion successful. Output file:", output_path)
    logging.info(f"Conversion successful: {output_path}")
    
def audio_converter(input_path, extension, single):
    logging.info(f"Starting audio conversion. Input: {input_path}, Extension: {extension}")
    
    # Get the file name and directory of the input video
    input_dir, input_name = os.path.split(input_path)
    input_name, _ = os.path.splitext(input_name)
    
    output_name = f"{input_name}.{extension}"
    if single:
        output_path = os.path.join(input_dir, output_name)
    else:
        output_dir = os.path.join((input_dir + f"_{extension}"))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_name)
         
    try:
        subprocess.run([FFMPEG_CMD, "-i", input_path, output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(" Conversion failed.")
        logging.error(f"Conversion failed for {input_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error during conversion for {input_path}: {e}", exc_info=True)
        return
    
    print("\n Conversion successful. Output file:", output_path)
    logging.info(f"Conversion successful: {output_path}")

        
def trim_media():
    logging.info("Starting media trimming")
    # Prompt for input file
    input_path = input(" Enter the path to the input file: ").strip().strip('"')
    
    if not os.path.exists(input_path):
        print(" The specified file does not exist.")
        return

    # Get file details
    input_dir, input_name = os.path.split(input_path)
    filename, ext = os.path.splitext(input_name)
    
    print("\n Enter time in format HH:MM:SS or seconds (e.g., 00:01:30 or 90)")
    start_time = input(" Start Time (default 00:00:00): ").strip()
    if not start_time:
        start_time = "00:00:00"
        
    end_time = input(" End Time (leave empty to keep rest): ").strip()
    
    output_name = f"{filename}_trimmed{ext}"
    output_path = os.path.join(input_dir, output_name)
    
    cmd = [FFMPEG_CMD, "-i", input_path, "-ss", start_time]
    
    if end_time:
        cmd.extend(["-to", end_time])
        
    # Use copy codec for fast trimming without re-encoding
    cmd.extend(["-c", "copy", "-y", output_path])
    
    start_time_proc = time.time()
    try:
        subprocess.run(cmd, check=True)
        print(f"\n Trimming successful. Output file: {output_path}")
        print(f" Time Taken: {(time.time() - start_time_proc):.2f} seconds")
        logging.info(f"Trimming successful: {output_path}")
    except subprocess.CalledProcessError as e:
        print(" Trimming failed. Check your time format.")
        logging.error(f"Trimming failed for {input_path}: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error during trimming for {input_path}: {e}", exc_info=True)
        return

if __name__ == "__main__":
    audio_extensions = (
        'aac', 'ac3', 'aif', 'aiff', 'alac', 'amr', 'ape', 'au', 'awb', 'flac', 'gsm', 'm4a',
        'm4b', 'm4p', 'mp3', 'ogg', 'oga', 'mogg', 'opus', 'ra', 'wav', 'wma', 'webm'
    )
    image_extensions = (
        'jpg', 'jpeg', 'png', 'tiff', 'tif', 'bmp', 'gif', 'webp', 'ico'
    )
    video_extensions = ('mp4', 'avi', 'mkv', 'mov', 'nix', 'org')
    
    while True:
        os.system("cls")
        os.system("color 0a")
        print(" =============================================")
        print("         Multi-Media-Master-Pro v3.0         ")
        print(" =============================================")
        print("                    Features                   ")
        print(" =============================================")

        print(" [1] Compress a video")
        print(" [2] Compress a directory of videos")
        print(" [3] Compress an image")
        print(" [4] Compress a directory of images")
        print(" [5] Record Screen without audio")
        print(" [6] Save output path for Screen Recording")
        print(" [7] Extract Audio from Video")
        print(" [8] Convert Audio to any format")
        print(" [9] Convert Image into any format")
        print(" [10] Trim Audio/Video")
        print(" [11] Exit")
        try:
            choice_input = input("\n >> ")
            choice = int(choice_input)
        except ValueError:
            print(" Enter only integers!")
            logging.warning(f"Invalid menu input: {choice_input}")
            continue
        except Exception as e:
            logging.error(f"Error reading menu input: {e}")
            continue
        
        try:
            if choice == 1:
                compress_video()

            elif choice == 2:
                # Input directory containing videos
                input_directory = input(" Enter the path of the input directory: ")

                # Remove surrounding quotes from input directory path
                input_directory = input_directory.strip('"')
                
                if not os.path.isdir(input_directory):
                    print(" Invalid directory path!")
                    logging.warning(f"Invalid directory path provided: {input_directory}")
                    input("\n Press enter to continue...")
                    continue

                # Choose compression level
                print("\n Select compression level:")
                print(" [1] Low compression (High quality, larger file)")
                print(" [2] Medium compression (Balanced quality/size)")
                print(" [3] High compression (Lower quality, smaller file)")
                
                try:
                    compression_choice = int(input(" Choose compression level (1-3): ").strip())
                except ValueError:
                    print(" Invalid input! Using medium compression by default.")
                    logging.warning("Invalid compression choice. Defaulting to 2.")
                    compression_choice = 2

                choice_ext = input(" Do you want to change the extension (Y/N): ").upper()
        
                given_extension = None
                if choice_ext == "Y":
                    given_extension = input(" Enter the extension without dot (.): ").lower().strip().strip(".")

                # Output directory for compressed videos
                output_directory = os.path.join(input_directory + "_compressed")
                
                start_time = time.time()
                if given_extension:
                    if given_extension in video_extensions:
                        # Compress videos
                        compress_videos(input_directory, output_directory, given_extension, compression_choice)
                    else:
                        print(" FFMPEG can't handle this video format!\n Try any other extensions.")
                        logging.warning(f"Invalid extension: {given_extension}")
                        input("\n Press enter to continue...")
                        continue
                else:
                    compress_videos(input_directory, output_directory, None, compression_choice)
                    
                print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
                
            elif choice == 3:
                compress_image()

            elif choice == 4:
                # Input directory containing images
                input_directory = input(" Enter the path of the input directory: ")

                # Remove surrounding quotes from input directory path
                input_directory = input_directory.strip('"')
                
                if not os.path.isdir(input_directory):
                    print(" Invalid directory path!")
                    logging.warning(f"Invalid directory path: {input_directory}")
                    input("\n Press enter to continue...")
                    continue

                # Choose compression level
                print("\n Select compression level:")
                print(" [1] Low compression (High quality, larger file)")
                print(" [2] Medium compression (Balanced quality/size)")
                print(" [3] High compression (Lower quality, smaller file)")
                
                try:
                    compression_choice = int(input(" Choose compression level (1-3): ").strip())
                except ValueError:
                    print(" Invalid input! Using medium compression by default.")
                    logging.warning("Invalid compression choice. Defaulting to 2.")
                    compression_choice = 2

                choice_ext = input(" Do you want to change the extension (Y/N): ").upper()
        
                given_extension = None
                if choice_ext == "Y":
                    given_extension = input(" Enter the extension without dot (.): ").lower().strip().strip(".")

                # Output directory for compressed images
                output_directory = os.path.join(input_directory + "_compressed")
                
                start_time = time.time()
                if given_extension:
                    if given_extension in image_extensions:
                        # Compress images
                        compress_images(input_directory, output_directory, given_extension, compression_choice)
                    else:
                        print(" FFMPEG can't handle this image format!\n Try any other extensions.")
                        logging.warning(f"Invalid extension: {given_extension}")
                        input("\n Press enter to continue...")
                        continue
                else:
                    compress_images(input_directory, output_directory, None, compression_choice)
                    
                print(f" Time Taken: {(time.time() - start_time):.2f} seconds")
                
            elif choice == 5:
                start_time = time.time()
                record_screen()
                
                output_dir_file = get_output_dir_file()
                if os.path.exists(output_dir_file):
                    with open(output_dir_file, 'r') as file:
                        output_directory = file.read().strip()
                    if output_directory and os.path.isdir(output_directory):
                        print(" Screen recording completed.")
                        print(f" Duration: {(time.time() - start_time):.2f} seconds")
                        os.system(f"explorer {output_directory}")
                input("\n Press enter to continue...")
                continue   
                
            elif choice == 6:
                output_path = input(" Enter output path for screen recording: ").strip()
                output_path = output_path.replace('"', '')
                if os.path.isdir(output_path):
                    try:
                        with open(get_output_dir_file(), 'w') as file:
                            file.write(output_path)
                        print(" Output path for screen recording is saved!")
                        logging.info(f"Screen recording output path saved: {output_path}")
                    except Exception as e:
                        print(f" Could not save output path: {e}")
                        logging.error(f"Failed to save output path: {e}")
                else:
                    print(" Output Path does not exist!")
                    logging.warning(f"Output path does not exist: {output_path}")
                    
            elif choice == 7:
                extract_audio()
                
            elif choice == 8:
                input_path = input(" File/Directory Path: ").strip()
                
                extension = input(" Extension to convert: ").lower().strip().strip(".")
            
                if extension not in audio_extensions:
                    print(" FFMPEG can't handle this video format!\n Try any other extensions.")
                    logging.warning(f"Invalid extension: {extension}")
                    input("\n Press enter to continue...")
                    continue
                
                file_or_dir = input(" Single File or Directory of Files (s/d): ").lower().strip()
                input_path = input_path.strip('"')
                
                start_time = time.time()
                if file_or_dir == "s":
                    audio_converter(input_path, extension, True)
                elif file_or_dir == "d":
                    if os.path.isdir(input_path):
                        files = [file for file in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, file))]
                        files = [file for file in files if file.lower().endswith(audio_extensions)]
                        for file in files:
                            audio_converter(os.path.join(input_path, file), extension, False)
                    else:
                        print(" Invalid directory path!")
                        logging.warning(f"Invalid directory: {input_path}")
                else:
                    print(" Invalid Choice!")
                    logging.warning(f"Invalid file/dir choice: {file_or_dir}")
                    input("\n Press enter to continue...")
                    continue
                print(f" Time Taken: {(time.time() - start_time):.2f} seconds")  
                
            elif choice == 9:
                input_path = input(" File/Directory Path: ").strip()
                
                extension = input(" Extension to convert: ").lower().strip().strip(".")
                if extension not in image_extensions:
                    print(" FFMPEG can't handle this video format!\n Try any other extensions.")
                    logging.warning(f"Invalid extension: {extension}")
                    input("\n Press enter to continue...")
                    continue
                
                file_or_dir = input(" Single File or Directory of Files (s/d): ").lower().strip()
                input_path = input_path.strip('"')
                
                start_time = time.time()
                if file_or_dir == "s":
                    image_converter(input_path, extension, True)
                elif file_or_dir == "d":
                    if os.path.isdir(input_path):
                        files = [file for file in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, file))]
                        files = [file for file in files if file.lower().endswith(image_extensions)]
                        for file in files:
                            image_converter(os.path.join(input_path, file), extension, False)
                    else:
                        print(" Invalid directory path!")
                        logging.warning(f"Invalid directory: {input_path}")
                else:
                    print(" Invalid Choice!")
                    logging.warning(f"Invalid file/dir choice: {file_or_dir}")
                    input("\n Press enter to continue...")
                    continue
                print(f" Time Taken: {(time.time() - start_time):.2f} seconds")    
    
            elif choice == 10:
                trim_media()
                
            elif choice == 11:
                logging.info("Exiting application by user request.")
                sys.exit(0)
                
            else:
                print("\n Invalid choice!")  
                logging.warning(f"Invalid choice number: {choice}")
                
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
            print(" An error occurred. Details have been logged.")
    
        input("\n Press enter to continue...")
