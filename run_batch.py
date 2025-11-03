#!/usr/bin/env python3
"""
Batch runner for Google Maps scraper to prevent system overload
"""
import os
import time
import subprocess

def run_batch(queries_file, batch_size=5):
    """Run scraper in small batches to prevent system overload"""
    
    # Read all queries
    with open(queries_file, 'r', encoding='utf-8') as f:
        all_queries = [line.strip() for line in f.readlines() if line.strip()]
    
    # Split into batches
    batches = [all_queries[i:i+batch_size] for i in range(0, len(all_queries), batch_size)]
    
    print(f"📊 Total queries: {len(all_queries)}")
    print(f"📦 Split into {len(batches)} batches of {batch_size} queries each")
    
    for batch_num, batch_queries in enumerate(batches, 1):
        print(f"\n🚀 Starting Batch {batch_num}/{len(batches)}")
        print(f"Queries: {', '.join(batch_queries)}")
        
        # Create temporary query file for this batch
        temp_file = f"temp_queries_batch_{batch_num}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(batch_queries))
        
        try:
            # Modify app.py to use temp file
            print("⏳ Running scraper...")
            
            # Create modified app.py for this batch
            with open("app.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace queries file
            content = content.replace(
                'QUERIES_FILE = os.path.join(os.path.dirname(__file__), "search_queries.txt")',
                f'QUERIES_FILE = "{temp_file}"'
            )
            
            # Write temporary app file
            with open("app_batch_temp.py", "w", encoding="utf-8") as f:
                f.write(content)
            
            result = subprocess.run(['python', 'app_batch_temp.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ Batch {batch_num} completed successfully")
            else:
                print(f"❌ Batch {batch_num} failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Batch {batch_num} timed out after 5 minutes")
        except Exception as e:
            print(f"❌ Error in batch {batch_num}: {e}")
        
        finally:
            # Clean up temp files
            for temp_file in [temp_file, "app_batch_temp.py"]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        
        # Wait between batches
        if batch_num < len(batches):
            print(f"⏳ Waiting 30 seconds before next batch...")
            time.sleep(30)
    
    print("\n🎉 All batches completed!")

if __name__ == "__main__":
    run_batch("search_queries.txt", batch_size=3)  # Run 3 queries at a time
