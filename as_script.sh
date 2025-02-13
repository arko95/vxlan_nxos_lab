#!/bin/bash

# Define directories
SOURCE_DIR="ansible_directory/ansible_generated"
DEST_DIR1="ans_vxlan_nxos/plays/host_vars"
DEST_DIR2="ans_vxlan_nxos/plays/group_vars"
PYTHON_SCRIPT="script.py"
ANSIBLE_DIR="ans_vxlan_nxos/plays"

# Ensure destination directories exist
mkdir -p "$DEST_DIR1"
mkdir -p "$DEST_DIR2"

# Name mapping
declare -A NAME_MAPPING=(
  ["LF1.yml"]="172.16.100.57.yml"
  ["LF2.yml"]="172.16.100.58.yml"
  ["LF3.yml"]="172.16.100.59.yml"
  ["SP1.yml"]="172.16.100.55.yml"
  ["SP2.yml"]="172.16.100.56.yml"
)

# Execute the Python script
echo "Executing Python script..."
python3 "$PYTHON_SCRIPT"

# Rename and copy specific files to DEST_DIR1
for ORIGINAL_NAME in "${!NAME_MAPPING[@]}"; do
  ORIGINAL_PATH="$SOURCE_DIR/$ORIGINAL_NAME"
  if [ -f "$ORIGINAL_PATH" ]; then
    NEW_NAME="${NAME_MAPPING[$ORIGINAL_NAME]}"
    echo "Copying and renaming $ORIGINAL_NAME to $NEW_NAME in $DEST_DIR1"
    cp "$ORIGINAL_PATH" "$DEST_DIR1/$NEW_NAME"
  else
    echo "Warning: File $ORIGINAL_NAME not found in $SOURCE_DIR"
  fi
done

# Copy spines.yml and leafs.yml to DEST_DIR2
for FILE in "spines.yml" "leafs.yml"; do
  SOURCE_PATH="$SOURCE_DIR/$FILE"
  if [ -f "$SOURCE_PATH" ]; then
    echo "Copying $FILE to $DEST_DIR2"
    cp "$SOURCE_PATH" "$DEST_DIR2/"
  else
    echo "Warning: File $FILE not found in $SOURCE_DIR"
  fi
done

# Execute the Ansible playbook
if [ -d "$ANSIBLE_DIR" ]; then
  echo "Changing to Ansible directory: $ANSIBLE_DIR"
  cd "$ANSIBLE_DIR" || exit

  if [ -f "main_vxlan.yml" ]; then
    echo "Executing Ansible playbook: main.yml"
    ansible-playbook main_vxlan.yml -i inven.yml -vvvv
  else
    echo "Error: main.yml not found in $ANSIBLE_DIR"
    exit 1
  fi
else
  echo "Error: Ansible directory $ANSIBLE_DIR does not exist."
  exit 1
fi

echo "All operations completed successfully."