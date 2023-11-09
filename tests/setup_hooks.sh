#!/bin/bash

echo "Writing call to tests/test.sh to .git/hooks/pre-push..."
PRE_PUSH_HOOK_PATH="./.git/hooks/pre-push"
echo "#!/bin/sh" >"${PRE_PUSH_HOOK_PATH}"
echo "./tests/test.sh" >>"${PRE_PUSH_HOOK_PATH}"
chmod +x "${PRE_PUSH_HOOK_PATH}" ||
    (echo "Error: Could not set executable permission on ${PRE_PUSH_HOOK_PATH}" \
        echo "Consider running chmod +x ${PRE_PUSH_HOOK_PATH} manually" &&
        exit 1)
echo "Done!"
