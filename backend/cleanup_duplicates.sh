#!/bin/bash
# Cleanup script for BrainSAIT OID System Backend
# This script removes duplicate files after successful migration to the unified implementation

echo "Starting cleanup of duplicate files..."

# Check if the unified main file exists and is executable
if [ -f "./unified_main.py" ]; then
    echo "✅ Found unified_main.py"

    # Make the unified file executable
    chmod +x ./unified_main.py

    # Backup original files before removal
    echo "Creating backup of original files..."
    mkdir -p ./backup_$(date +"%Y%m%d_%H%M%S")

    for file in main.py main_simple.py enhanced_unified_service.py unified_healthcare_service.py requirements-minimal.txt requirements-python311.txt requirements-simple.txt requirements.txt; do
        if [ -f "./$file" ]; then
            cp ./$file ./backup_$(date +"%Y%m%d_%H%M%S")/
            echo "✅ Backed up $file"
        fi
    done

    # Remove duplicate files
    echo "Removing duplicate files..."
    for file in main_simple.py enhanced_unified_service.py unified_healthcare_service.py requirements-minimal.txt requirements-python311.txt requirements-simple.txt requirements.txt; do
        if [ -f "./$file" ]; then
            rm ./$file
            echo "🗑️  Removed $file"
        fi
    done

    # Rename the unified file to main.py
    mv ./unified_main.py ./main.py
    echo "✅ Renamed unified_main.py to main.py"

    # Create symbolic links to requirements_unified.txt
    ln -sf requirements_unified.txt requirements.txt
    echo "✅ Created symlink for requirements.txt"

    echo "✅ Cleanup complete! The unified implementation is now active."
    echo "To run the application, use: python3 main.py"
else
    echo "❌ Error: unified_main.py not found. Aborting cleanup."
    exit 1
fi
