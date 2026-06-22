#!/bin/bash
# Test Update v2 — Run this after v1 to trigger a second deployment

echo "Applying v2 update: Changing hero background and version badge..."

# Update the version
sed -i 's/v1.0.0 - Pipeline Test Update/v2.0.0 - Auto-Scaling Verified/' app/index.html
sed -i 's/LIVE ON AWS - v1.0.0/LIVE ON AWS - v2.0.0/' app/index.html

echo "Done! Now run:"
echo "  git add app/index.html"
echo "  git commit -m 'test: pipeline test update v2'"
echo "  git push origin master"
echo ""
echo "Then watch the pipeline at:"
echo "  https://console.aws.amazon.com/codesuite/codepipeline/pipelines/suyashkadam-prod-pipeline/view?region=us-east-1"
