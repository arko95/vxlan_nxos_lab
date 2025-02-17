#!/bin/bash
echo "Running Python validation..."
./validate_json.py input.json
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "Python validation passed. Executing the next script..."
    ./next_script.sh
else
    echo "Python validation failed. Aborting the pipeline."
    exit 1
fi