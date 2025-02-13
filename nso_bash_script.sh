#!/bin/bash

# Read the content of input.json into a variable
CONTENT_FILE_JSON=$(cat input.json)

# Create the required JSON structure dynamically
FINAL_JSON=$(cat <<EOF
{
    "vxlan-srv:vxlan-srv": [
        $CONTENT_FILE_JSON
    ]
}
EOF
)

# Use the dynamically generated JSON in the curl command
curl --location --request POST 'http://localhost:8090/restconf/data' \
--header 'Accept: application/yang-data+json, application/vnd.yang.collection+json, application/yang-patch+json' \
--header 'Content-Type: application/yang-data+json' \
-u "admin:admin" \
--data "$FINAL_JSON"