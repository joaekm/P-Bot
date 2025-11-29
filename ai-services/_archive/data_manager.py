import os
import time
import shutil
import logging
import rag_service  # Uses the existing RAG service logic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DataManager")

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FAILED_DIR = os.path.join(DATA_DIR, "failed")

# Ensure directories exist
for directory in [RAW_DIR, PROCESSED_DIR, FAILED_DIR]:
    os.makedirs(directory, exist_ok=True)

def process_file_with_path(source_path, rel_path, filename):
    """Processes a single file from raw directory or subdirectory."""
    
    logger.info(f"Starting processing of: {rel_path}")

    try:
        # 1. Use rag_service to extract, chunk, and index
        # Category is auto-detected from path (roles/, levels/, rules/)
        success = rag_service.add_document(source_path, filename)

        if success:
            # 2. If successful: Move to 'processed' (preserve subfolder structure)
            # Get the subdirectory (e.g., 'roles', 'levels', 'rules')
            subdir = os.path.dirname(rel_path)
            if subdir:
                dest_dir = os.path.join(PROCESSED_DIR, subdir)
                os.makedirs(dest_dir, exist_ok=True)
            else:
                dest_dir = PROCESSED_DIR
            
            dest_path = os.path.join(dest_dir, filename)
            # Handle overwrite if file exists in processed
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
                
            shutil.move(source_path, dest_path)
            logger.info(f"DONE: {rel_path} indexed and moved to 'processed'.")
        else:
            # 3. If rag_service returns False (e.g., no text found)
            raise Exception("No text could be extracted or indexing failed.")

    except Exception as e:
        # 4. If error: Move to 'failed' (preserve subfolder structure)
        logger.error(f"ERROR: Could not process {rel_path}. Reason: {str(e)}")
        subdir = os.path.dirname(rel_path)
        if subdir:
            dest_dir = os.path.join(FAILED_DIR, subdir)
            os.makedirs(dest_dir, exist_ok=True)
        else:
            dest_dir = FAILED_DIR
            
        dest_path = os.path.join(dest_dir, filename)
        # Handle overwrite if file exists in failed
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
            
        shutil.move(source_path, dest_path)

def run_batch_job():
    """Runs through all files in the raw folder and subfolders (roles/, levels/, rules/)."""
    files_to_process = []
    
    # Walk through raw directory and all subdirectories
    for root, dirs, files in os.walk(RAW_DIR):
        for filename in files:
            # Ignore hidden files (e.g. .DS_Store)
            if filename.startswith('.'):
                continue
            
            full_path = os.path.join(root, filename)
            # Get relative path from RAW_DIR for display
            rel_path = os.path.relpath(full_path, RAW_DIR)
            files_to_process.append((full_path, rel_path, filename))
    
    if not files_to_process:
        logger.info("No new files in data/raw to process.")
        return

    logger.info(f"Found {len(files_to_process)} files to process...")
    
    for full_path, rel_path, filename in files_to_process:
        process_file_with_path(full_path, rel_path, filename)

if __name__ == "__main__":
    print("--- Adda Data Manager ---")
    print(f"Watching directory: {RAW_DIR}")
    print("Running batch job now...")
    
    run_batch_job()
    
    print("--- Done ---")


