import os
import re
import shutil
import numpy as np
from pathlib import Path
from data_handling import compile_driver_data


def main():
    # 1. Dynamically discover the root directory and navigate to 2025 folder
    script_dir = Path(__file__).resolve().parent
    data_dir = script_dir / "2025"
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Could not find '2025' folder at {data_dir}")
    
    print(f"Script directory: {script_dir}")
    print(f"Data directory: {data_dir}")
    
    # 2. Clean the workspace - delete existing db/ folder in root
    db_dir = script_dir / "db"
    if db_dir.exists():
        print(f"Removing existing database folder: {db_dir}")
        shutil.rmtree(db_dir)
    
    # Create fresh db directory
    db_dir.mkdir(exist_ok=True)
    print(f"Created fresh database folder: {db_dir}")
    
    # 3. Iterate through data
    # Pattern for 3-letter driver codes
    driver_pattern = re.compile(r'^[A-Z]{3}$')
    
    # Find all Grand Prix directories in the 2025 folder
    grand_prix_dirs = [d for d in data_dir.iterdir() 
                       if d.is_dir() and d.name.endswith('Grand Prix')]
    
    print(f"\nFound {len(grand_prix_dirs)} Grand Prix directories in 2025 folder")
    
    # Track statistics
    total_processed = 0
    total_failed = 0
    
    for gp_dir in grand_prix_dirs:
        race_name = gp_dir.name
        print(f"\n{'='*60}")
        print(f"Processing: {race_name}")
        print(f"{'='*60}")
        
        # Look for the Race subdirectory
        race_dir = gp_dir / "Race"
        if not race_dir.exists():
            print(f"  Warning: No 'Race' folder found in {race_name}, skipping")
            continue
        
        # Find all driver code subdirectories in the Race folder
        driver_dirs = [d for d in race_dir.iterdir() 
                      if d.is_dir() and driver_pattern.match(d.name)]
        
        print(f"Found {len(driver_dirs)} drivers in {race_name}/Race")
        
        for driver_dir in driver_dirs:
            driver_code = driver_dir.name
            
            try:
                # 4. Process and save data
                print(f"  Processing: {race_name} - {driver_code}...", end=" ")
                
                # Call the compile function
                data = compile_driver_data(race_name, driver_code)
                
                # Create output directory structure (only race folder)
                output_dir = db_dir / race_name
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Save the data as driver_code.npy
                output_path = output_dir / f"{driver_code}.npy"
                np.save(output_path, data)
                print(f"{driver_code} successful")
                
            except Exception as e:
                # 5. Handle errors gracefully
                print(f"✗ Failed: {str(e)}")
                total_failed += 1
                continue
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total successfully processed: {total_processed}")
    print(f"Total failed: {total_failed}")
    print(f"Database location: {db_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()