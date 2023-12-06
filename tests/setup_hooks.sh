#!/bin/bash

REPO_ROOT=$(git rev-parse --show-toplevel)

echo "Writing call to ${REPO_ROOT}/tests/test.sh to .git/hooks/pre-push..."
PRE_PUSH_HOOK_PATH="${REPO_ROOT}/.git/hooks/pre-push"
echo "#!/bin/sh" >"${PRE_PUSH_HOOK_PATH}"
echo "${REPO_ROOT}/tests/test.sh" >>"${PRE_PUSH_HOOK_PATH}"
chmod +x "${PRE_PUSH_HOOK_PATH}" ||
    (echo "Error: Could not set executable permission on ${PRE_PUSH_HOOK_PATH}" \
        echo "Consider running chmod +x ${PRE_PUSH_HOOK_PATH} manually" &&
        exit 1)
echo "Done!"
