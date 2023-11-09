#!/bin/bash

echo "Writing call to tests/test.sh to .git/hooks/pre-push..."
echo "#!/bin/sh" >.git/hooks/pre-push
echo "./tests/test.sh" >>.git/hooks/pre-push
chmod +x .git/hooks/pre-push
