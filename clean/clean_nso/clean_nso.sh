#!/usr/bin/env bash

# Read the value of the "name" key from the JSON file into a variable
NAME=$(jq -r '.name' input.json)

# Print the variable to confirm

URL="http://localhost:8090/restconf/data/vxlan-srv:vxlan-srv=$NAME/un-deploy"
curl --location --request POST $URL \
--header 'Accept: application/yang-data+json, application/vnd.yang.collection+json, application/yang-patch+json' \
--header 'Content-Type: application/yang-data+json' \
-u "admin:admin" --data ''