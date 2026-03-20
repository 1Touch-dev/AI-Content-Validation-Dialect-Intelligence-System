import os
import sys
import glob
import time
import pandas as pd
import concurrent.futures

# Make sure we can import video module safely
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from video_validator import VideoValidator
from services.config import REPORTS_DIR

def process_single_video(video_path, expected_topic):
    # Instantiate a local Validator per worker since PyTorch MPS/CUDA
    # context is generally un-safe across pure multiprocessing forks.
    # We enforce CPU for broad concurrent scalability on Mac. 
    validator = VideoValidator(device="cpu")
    try:
        result = validator.validate_video(video_path, expected_topic)
        return result
    except Exception as e:
        print(f"Error processing {os.path.basename(video_path)}: {e}")
        return None

def batch_process(folder_path, expected_topic, max_workers=2):
    videos = glob.glob(os.path.join(folder_path, "*.mp4"))
    
    if not videos:
        print(f"No .mp4 files found in {folder_path}")
        return
        
    print(f"Found {len(videos)} videos to process in {folder_path} via {max_workers} threads...")
    
    results = []
    start_time = time.time()
    
    # ProcessPoolExecutor manages distinct Python instances protecting PyTorch context integrity natively
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_video, v, expected_topic): v for v in videos}
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                
    total_time = time.time() - start_time
    print(f"\nBatch Job Complete: Processed {len(results)}/{len(videos)} correctly in {total_time:.2f}s")
    
    if results:
        df = pd.DataFrame(results)
        df = df[['video_file', 'dialect_predicted', 'dialect_confidence', 'content_match_score', 'validation_status']]
        df.rename(columns={'video_file': 'video_name', 'dialect_predicted': 'dialect_prediction'}, inplace=True)
        
        out_csv = os.path.join(REPORTS_DIR, "batch_validation_results.csv")
        os.makedirs(REPORTS_DIR, exist_ok=True)
        df.to_csv(out_csv, index=False)
        print(f"Results securely exported to {out_csv}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Concurrent Validation Batch Processor")
    parser.add_argument("--folder", type=str, required=True, help="Target localized directory containing Marketing MP4 videos.")
    parser.add_argument("--topic", type=str, default="Honduran football player", help="Base expected contextual visual theme.")
    parser.add_argument("--workers", type=int, default=2, help="Parallel worker nodes to scale ML orchestration.")
    args = parser.parse_args()
    
    batch_process(args.folder, args.topic, args.workers)
