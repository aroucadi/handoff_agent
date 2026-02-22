#!/bin/bash
set -e

MANIFEST_PATH="synapse.yaml"
if [ ! -f "$MANIFEST_PATH" ]; then
    echo "Could not find $MANIFEST_PATH at root." >&2
    exit 1
fi

GLOBAL_VERSION=$(grep -E '^global_version:[[:space:]]*' "$MANIFEST_PATH" | awk -F ':' '{print $2}' | xargs)

if [ -z "$GLOBAL_VERSION" ]; then
    echo "Could not parse 'global_version' from synapse.yaml" >&2
    exit 1
fi

echo -e "\033[36m=============================================\033[0m"
echo -e "\033[36m🔄 Disseminating Global Version: v$GLOBAL_VERSION\033[0m"
echo -e "\033[36m=============================================\033[0m"

PACKAGE_JSON="frontend/package.json"
if [ -f "$PACKAGE_JSON" ]; then
    echo "-> Updating $PACKAGE_JSON"
    sed -i.bak -E 's/"version": "[^"]+"/"version": "'"$GLOBAL_VERSION"'"/' "$PACKAGE_JSON"
    rm -f "${PACKAGE_JSON}.bak"
fi

update_fastapi_version() {
    local FILE="$1"
    if [ -f "$FILE" ]; then
        echo "-> Updating $FILE"
        sed -i.bak -E 's/version="[^"]+"/version="'"$GLOBAL_VERSION"'"/' "$FILE"
        rm -f "${FILE}.bak"
    fi
}

update_fastapi_version "backend/main.py"
update_fastapi_version "graph-generator/main.py"
update_fastapi_version "crm-simulator/main.py"

echo -e "\n\033[32m✅ Successfully synchronized all monorepo pieces to v$GLOBAL_VERSION.\033[0m"
echo -e "\033[33mDon't forget to push a git tag for v$GLOBAL_VERSION!\033[0m"
