# <center> Multi-Media-Master-Pro v3.1 </center>

**Multi-Media-Master-Pro** is a versatile media processing tool that offers a range of functionalities including video compression, image compression, screen recording, audio extraction, and media format conversion. It's designed to simplify and enhance your media management tasks, all within a user-friendly interface.

---

## Features Overview

### [1] Compress a Video
Compress a single video file to reduce its size with customizable compression levels. Choose from Low, Medium, or High compression based on your quality vs. size requirements. The tool provides detailed information after compression including original size, compressed size, size reduction percentage, and processing time.

### [2] Compress a Directory of Videos
Batch compress all videos within a specified directory. This feature generates a CSV file with detailed compression statistics for each video, including file sizes, remaining size percentage, and size reduction percentage. Perfect for processing multiple videos efficiently.

### [3] Compress an Image
Compress a single image file with three compression levels (Low, Medium, High) to balance quality and file size. After compression, you'll receive detailed information about the original size, compressed size, size reduction, and processing time.

### [4] Compress a Directory of Images
Batch compress all images within a specified directory. Similar to video batch compression, this feature generates a CSV file with comprehensive compression data for each image, making it easy to track compression results across multiple files.

### [5] Record Screen without Audio
Capture your screen activities without recording any audio. The recording duration is displayed when you stop the recording. This feature is useful for creating tutorials, presentations, or any screen-based demonstrations where audio isn't needed.

### [6] Save Output Path for Screen Recording
Set and save a custom output path for your screen recordings. This feature provides flexibility and organization, allowing users to choose where their screen recordings are stored by default.

### [7] Extract Audio from Video
Extract the audio track from any video file and save it as a standalone MP3 file. The tool displays the processing time after extraction. This is useful for users who want to isolate music, speeches, or any audio content from videos.

### [8] Convert Audio to Any Format
Convert audio files from one format to another, supporting various formats like MP3, WAV, AAC, FLAC, OGG, etc. You can convert single files or entire directories. Processing time is displayed after conversion.

### [9] Convert Image into Any Format
Convert image files from one format to another, supporting formats like JPG, PNG, BMP, GIF, WEBP, etc. You can convert single files or entire directories. Processing time is displayed after conversion.

### [10] Trim Audio/Video
Trim audio or video files by specifying start and end times. This feature uses fast processing techniques to extract segments without re-encoding (where possible), preserving original quality.


## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/Muhammad-Ilyas-Ibrahim/Multi-Media-Master-Pro-CLI.git
    cd Multi-Media-Master-Pro-CLI
    ```

## Usage

1. ### **Run the Script:**
    ```bash
    python MultiMediaMasterPro_CLI.py
    ```

2. ### **How to Use**

   #### **[1] Compress a Video**

   1. **Select the Option:** Choose the option `[1] Compress a video` from the menu.
   2. **Input the Video File Path:** Enter the full path of the video file you wish to compress.
   3. **Choose Compression Level:** Select from:
      - `[1] Low bitrate compression (CRF 20, larger file size)` - Best quality, larger file
      - `[2] Medium bitrate compression (CRF 25, balanced file size)` - Balanced quality and size
      - `[3] High bitrate compression (CRF 30, smaller file size)` - Smaller file, lower quality
   4. **Change Extension (Optional):** Choose whether to change the output file extension (Y/N).
   5. **Run the Compression:** The script will compress the video and display detailed information:
      - Compression level used
      - Output file path
      - Original file size (KB)
      - Compressed file size (KB)
      - Remaining size percentage
      - Size reduction percentage
      - Processing time (seconds)
   6. **Automatic Folder Opening:** The output folder will automatically open in Windows Explorer (unless it's the Desktop).

   **Use Case:**
   This feature is helpful when you want to reduce the file size of a single video to save storage space or make it easier to upload and share, with full control over quality vs. size trade-offs.

   #### **[2] Compress a Directory of Videos**

   1. **Select the Option:** Choose the option `[2] Compress a directory of videos` from the menu.
   2. **Input the Directory Path:** Enter the path to the directory containing the videos you want to compress.
   3. **Choose Compression Level:** Select from Low, Medium, or High compression (same as single video compression).
   4. **Change Extension (Optional):** Choose whether to change the output file extension for all videos (Y/N).
   5. **Run the Batch Compression:** The script will:
      - Compress all videos in the directory
      - Display progress for each video with size reduction percentage
      - Generate a CSV file (`compression_data.csv`) containing:
        - File name
        - Original file size (KB)
        - Compressed file size (KB)
        - Remaining size percentage
        - Size reduction percentage
      - Display total processing time
      - Automatically open the output folder in Windows Explorer (unless it's the Desktop)

   **Use Case:**
   Ideal for users who have multiple videos that need compression, saving time by processing all videos in a batch with comprehensive statistics tracking.

   #### **[3] Compress an Image**

   1. **Select the Option:** Choose the option `[3] Compress an image` from the menu.
   2. **Input the Image File Path:** Enter the full path of the image file you wish to compress.
   3. **Choose Compression Level:** Select from:
      - `[1] Low compression (Quality 95, larger file size)` - Best quality, larger file
      - `[2] Medium compression (Quality 85, balanced file size)` - Balanced quality and size
      - `[3] High compression (Quality 70, smaller file size)` - Smaller file, lower quality
   4. **Change Extension (Optional):** Choose whether to change the output file extension (Y/N).
   5. **Run the Compression:** The script will compress the image and display detailed information:
      - Compression level used
      - Output file path
      - Original file size (KB)
      - Compressed file size (KB)
      - Remaining size percentage
      - Size reduction percentage
      - Processing time (seconds)
   6. **Automatic Folder Opening:** The output folder will automatically open in Windows Explorer (unless it's the Desktop).

   **Use Case:**
   Perfect for reducing image file sizes for web use, email attachments, or storage optimization while maintaining control over quality.

   #### **[4] Compress a Directory of Images**

   1. **Select the Option:** Choose the option `[4] Compress a directory of images` from the menu.
   2. **Input the Directory Path:** Enter the path to the directory containing the images you want to compress.
   3. **Choose Compression Level:** Select from Low, Medium, or High compression (same as single image compression).
   4. **Change Extension (Optional):** Choose whether to change the output file extension for all images (Y/N).
   5. **Run the Batch Compression:** The script will:
      - Compress all images in the directory
      - Display progress for each image with size reduction percentage
      - Generate a CSV file (`compression_data.csv`) containing:
        - File name
        - Original file size (KB)
        - Compressed file size (KB)
        - Remaining size percentage
        - Size reduction percentage
      - Display total processing time
      - Automatically open the output folder in Windows Explorer (unless it's the Desktop)

   **Use Case:**
   Ideal for batch processing multiple images, such as photo galleries, website assets, or bulk image optimization projects.

   #### **[5] Record Screen without Audio**

   1. **Select the Option:** Choose the option `[5] Record Screen without audio` from the menu.
   2. **Start Recording:** The screen recording will begin immediately using the saved output path (set via option 6).
   3. **Stop Recording:** Press `Ctrl + C` to stop the recording.
   4. **View Results:** After stopping, the tool will display:
      - Recording completion message
      - Recording duration (seconds)
      - Automatically open the output folder in Windows Explorer

   **Note:** Make sure to set the output path first using option `[6] Save output path for Screen Recording`.

   **Use Case:**
   Great for creating screen tutorials, software demonstrations, or presentations where audio isn't required.

   #### **[6] Save Output Path for Screen Recording**

   1. **Select the Option:** Choose the option `[6] Save output path for Screen Recording` from the menu.
   2. **Input Desired Path:** Enter the path where you want all future screen recordings to be saved by default.
   3. **Path Validation:** The tool will verify that the path exists before saving it.

   **Use Case:**
   This feature provides convenience and organization by allowing you to pre-set the output location for your screen recordings.

   #### **[7] Extract Audio from Video**

   1. **Select the Option:** Choose the option `[7] Extract Audio from Video` from the menu.
   2. **Input the Video File Path:** Enter the full path of the video file from which you want to extract audio.
   3. **Run Audio Extraction:** The script will:
      - Extract the audio track and save it as an MP3 file in the same directory as the source video
      - Display the output file path
      - Show the processing time (seconds)

   **Use Case:**
   Useful for extracting music, speeches, or sound effects from videos for use in other projects or playback.

   #### **[8] Convert Audio to Any Format**

   1. **Select the Option:** Choose the option `[8] Convert Audio to any format` from the menu.
   2. **Input File/Directory Path:** Enter the full path of the audio file or directory containing audio files.
   3. **Specify Desired Format:** Enter the desired output format (e.g., MP3, WAV, AAC, FLAC, OGG) without the dot.
   4. **Choose Processing Mode:** Select:
      - `s` for Single File - converts one file and saves it in the same directory
      - `d` for Directory - converts all audio files in the directory and saves them in a new subdirectory
   5. **Run Conversion:** The script will:
      - Convert the audio file(s) to the specified format
      - Display the output file path(s)
      - Show the total processing time (seconds)

   **Supported Formats:** AAC, AC3, AIF, AIFF, ALAC, AMR, APE, AU, AWB, FLAC, GSM, M4A, M4B, M4P, MP3, OGG, OGA, MOGG, OPUS, RA, WAV, WMA, WEBM

   **Use Case:**
   Essential for users who need to convert audio files to different formats for compatibility with various devices or software.

   #### **[9] Convert Image into Any Format**

   1. **Select the Option:** Choose the option `[9] Convert Image into any format` from the menu.
   2. **Input File/Directory Path:** Enter the full path of the image file or directory containing image files.
   3. **Specify Desired Format:** Enter the desired output format (e.g., JPG, PNG, BMP, GIF, WEBP) without the dot.
   4. **Choose Processing Mode:** Select:
      - `s` for Single File - converts one file and saves it in the same directory
      - `d` for Directory - converts all image files in the directory and saves them in a new subdirectory
   5. **Run Conversion:** The script will:
      - Convert the image file(s) to the specified format
      - Display the output file path(s)
      - Show the total processing time (seconds)

   **Supported Formats:** JPG, JPEG, PNG, TIFF, TIF, BMP, GIF, WEBP, ICO

   **Use Case:**
   Great for users who need to convert images for specific needs, such as web use, printing, or sharing.

   #### **[10] Trim Audio/Video**

   1. **Select the Option:** Choose the option `[10] Trim Audio/Video` from the menu.
   2. **Input File Path:** Enter the full path of the audio or video file.
   3. **Set Start Time:** Enter the start time (e.g., `00:01:30` or `90` seconds). Default is `00:00:00`.
   4. **Set End Time:** Enter the end time. Leave empty to keep the rest of the media.
   5. **Run Trimming:** The script will extract the segment and save it as `_trimmed`.

   **Use Case:**
   Perfect for creating clips, removing unwanted intros/outros, or shortening content for social media.

---

## Enhanced User Experience Features

### Detailed Output Information
After each operation, the tool provides comprehensive information to help you understand the results:

- **File Size Information:** Original and compressed file sizes in KB
- **Compression Statistics:** Remaining size percentage and size reduction percentage
- **Processing Time:** Time taken for each operation in seconds
- **Output Paths:** Clear indication of where files are saved
- **Progress Updates:** Real-time progress for batch operations

### CSV Reports for Batch Operations
When compressing directories of videos or images, the tool automatically generates a `compression_data.csv` file containing:
- File name
- Original file size (KB)
- Compressed file size (KB)
- Remaining size percentage
- Size reduction percentage

This CSV file makes it easy to analyze compression results across multiple files and track optimization efforts.

### Automatic Folder Opening
After operations complete, the tool automatically opens the output folder in Windows Explorer (unless the output is on the Desktop), making it easy to access your processed files immediately.

### Robust Logging & Error Handling
The application now features a comprehensive logging system. All activities and errors are recorded in `app_debug.log` (created in the same directory), helping you troubleshoot issues. The tool is also protected against unexpected crashes, ensuring a smooth user experience even when errors occur.

### Smart FFmpeg Detection
No need for complex PATH configurations. The tool intelligently locates `ffmpeg.exe` whether it's in the system PATH, the current directory, or bundled within the application (PyInstaller compatibility), ensuring seamless execution.

### Compression Level Options
Both video and image compression offer three levels:
- **Low Compression:** Best quality, larger file size
- **Medium Compression:** Balanced quality and file size (default)
- **High Compression:** Smaller file size, lower quality

### Extension Flexibility
You can optionally change file extensions during compression, allowing you to convert formats while compressing (e.g., compress a video and change it from .avi to .mp4).

---

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
