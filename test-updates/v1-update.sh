#!/bin/bash
# Test Update v1 — Run this to simulate a change and trigger the pipeline

echo "Applying v1 update: Adding deployment version badge..."

# Inject a version badge into the hero section
sed -i 's/Available for opportunities/v1.0.0 - Pipeline Test Update/' app/index.html

# Update the banner text
sed -i 's/LIVE ON AWS/LIVE ON AWS - v1.0.0/' app/index.html

echo "Done! Now run:"
echo "  git add app/index.html"
echo "  git commit -m 'test: pipeline test update v1'"
echo "  git push origin master"
echo ""
echo "Then watch the pipeline at:"
echo "  https://console.aws.amazon.com/codesuite/codepipeline/pipelines/suyashkadam-prod-pipeline/view?region=us-east-1"
