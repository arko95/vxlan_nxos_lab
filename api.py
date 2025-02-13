from flask import Flask, request, jsonify
import os
import json
import subprocess

app = Flask(__name__)

# Data storage for each endpoint and file type
data_store = {
    "ansible_vxlan": {"input": [], "test": []},
    "terraform_vxlan": {"input": [], "test": []},
    "nso_vxlan": {"input": [], "test": []}
}

scripts = {
    "ansible_vxlan": "./as_script.sh",
    "terraform_vxlan": "./tf_script.sh",
    "nso_vxlan": "./nso_bash_script.sh"
}

# Path to the pyATS directory
pyats_directory = "../vxlan_pyats"

# pyATS command template
pyats_command = "pyats run job vxlan_job.py --testbed-file testbed.yml --no-archive --archive-dir . --archive-name vxlan_lab.tar"

# Helper function to validate endpoints
def validate_endpoint(endpoint):
    if endpoint not in data_store:
        return jsonify({"error": f"Invalid endpoint '{endpoint}'"}), 404

@app.route('/<string:endpoint>', methods=['GET', 'POST'])
def handle_vxlan(endpoint):
    # Validate the endpoint
    validation_response = validate_endpoint(endpoint)
    if validation_response:
        return validation_response

    if request.method == 'GET':
        # Return stored data for the endpoint
        return jsonify(data_store[endpoint]), 200

    if request.method == 'POST':
        # Get the file type from query parameters (default to "input")
        file_type = request.args.get("file_type", "input")
        if file_type not in ["input", "test"]:
            return jsonify({"error": "Invalid file_type. Use 'input' or 'test'."}), 400

        # Determine the expected file name based on file_type
        file_name = f"{file_type}.json"

        # Check if the expected file is in the request
        if file_name not in request.files:
            return jsonify({"error": f"File '{file_name}' is required"}), 400
        
        file = request.files[file_name]
        if file.filename == '':
            return jsonify({"error": "No file uploaded"}), 400

        try:
            # Read the JSON data from the uploaded file
            file_content = json.load(file)
            
            # Append data to the corresponding endpoint's data store
            data_store[endpoint][file_type].append(file_content)

            if file_type == "input":
                # Execute the corresponding bash script
                script_path = scripts[endpoint]
                if not os.path.exists(script_path):
                    return jsonify({"error": f"Script '{script_path}' not found"}), 500
                
                try:
                    result = subprocess.run([script_path], capture_output=True, text=True, check=True)
                    script_output = result.stdout
                except subprocess.CalledProcessError as e:
                    return jsonify({
                        "error": "Error executing script",
                        "script_output": e.stderr
                    }), 500

                return jsonify({
                    "message": f"Data successfully added to {endpoint} ({file_type}) and script executed",
                    "data": file_content,
                    "script_output": script_output
                }), 201

            elif file_type == "test":
                # Execute the pyATS command in the specified directory, passing VNIS_IPS
                if not os.path.exists(pyats_directory):
                    return jsonify({"error": f"pyATS directory '{pyats_directory}' not found"}), 500

                try:
                    # Convert JSON content to a string to set as environment variable
                    vnis_ips = json.dumps(file_content)

                    # Add VNIS_IPS to the environment variables
                    env = os.environ.copy()
                    env["VNIS_IPS"] = vnis_ips

                    result = subprocess.run(
                        pyats_command,
                        shell=True,
                        cwd=pyats_directory,
                        env=env,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    script_output = result.stdout
                except subprocess.CalledProcessError as e:
                    return jsonify({
                        "error": "Error executing pyATS command",
                        "script_output": e.stderr
                    }), 500

                return jsonify({
                    "message": f"Data successfully added to {endpoint} ({file_type}) and pyATS command executed with VNIS_IPS",
                    "data": file_content,
                    "script_output": script_output
                }), 201

        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON file"}), 400
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)