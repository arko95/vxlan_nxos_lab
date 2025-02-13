#!/bin/bash

# Define directories
SOURCE_DIR="terraform_directory/terraform_generated"
DEST_DIR="tf_vxlan_nxos/nac-nxos/data"
TERRAFORM_DIR="tf_vxlan_nxos/nac-nxos"
PYTHON_SCRIPT="tf_script.py"

#clean services files
echo "Cleaning directories to work on directory: $TERRAFORM_DIR/data"
find "$TERRAFORM_DIR/data" -type f \( -name "*service_l2_vni*" -o -name "*service_l3_vni*" -o -name "*interface_templates*" \) -delete

# Ensure destination directory exists
mkdir -p "$DEST_DIR"

# Execute the Python script
echo "Executing Python script..."
python3 "$PYTHON_SCRIPT"

# Find all YAML files in the source directory and copy them to the destination directory
echo "Copying YAML files to $DEST_DIR..."
find "$SOURCE_DIR" -type f -name "*.yaml" -exec cp {} "$DEST_DIR" \;

echo "Operation completed successfully."

if [ -d "$TERRAFORM_DIR" ]; then
  echo "Changing to Terraform directory: $TERRAFORM_DIR"
  cd "$TERRAFORM_DIR" || exit

  echo "Applying Terraform configuration..."
  terraform init
  terraform apply -auto-approve

else
  echo "Error: Terraform directory $TERRAFORM_DIR does not exist."
  exit 1
fi