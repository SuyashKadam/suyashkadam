#!/usr/bin/env bash
# ============================================================
# S3 REMOTE STATE RECOVERY SCRIPT
# Use this when your remote state is in S3 and you need
# to roll back to a previous version after a bad apply.
#
# Prerequisites:
#   - aws cli configured
#   - terraform initialized with S3 backend
#   - S3 versioning enabled on your state bucket
# ============================================================

# ── CONFIG — change these to match your setup ───────────────
BUCKET="yourname-terraform-state-2024"
STATE_KEY="dev/terraform.tfstate"
REGION="us-east-1"
ENV_DIR="../../../environments/dev"   # path to your terraform env

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         S3 STATE RECOVERY — STEP BY STEP            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: List all versions of the state file ─────────────
echo "▶ STEP 1: List all state file versions in S3"
echo "──────────────────────────────────────────────────────"
echo "Running: aws s3api list-object-versions"
echo ""

aws s3api list-object-versions \
  --bucket "$BUCKET" \
  --prefix "$STATE_KEY" \
  --region "$REGION" \
  --query 'Versions[*].{VersionId:VersionId,LastModified:LastModified,IsLatest:IsLatest}' \
  --output table

echo ""
echo "The LATEST version is the broken one (v2 apply just wrote it)."
echo "Find the version JUST BEFORE the latest — that's your v1 state."
echo ""
echo "Press Enter to continue..."
read

# ── Step 2: Download the previous (good) version ────────────
echo "▶ STEP 2: Download the previous good state version"
echo "──────────────────────────────────────────────────────"
echo "Copy the VersionId from above output and paste it here."
read -p "Enter the VersionId of the GOOD (previous) state: " GOOD_VERSION

if [ -z "$GOOD_VERSION" ]; then
  echo "No version ID provided. Exiting."
  exit 1
fi

# Download the specific version
aws s3api get-object \
  --bucket "$BUCKET" \
  --key "$STATE_KEY" \
  --version-id "$GOOD_VERSION" \
  --region "$REGION" \
  terraform.tfstate.recovered

echo "  ✓ Downloaded to: terraform.tfstate.recovered"
echo ""
echo "Preview the recovered state (check serial number and resources):"
cat terraform.tfstate.recovered | python3 -m json.tool | grep -E '"serial"|"type"|"name"' | head -30
echo ""
echo "Press Enter to continue..."
read

# ── Step 3: Push the recovered state back to S3 ─────────────
echo "▶ STEP 3: Push recovered state to S3 (overwrite broken state)"
echo "──────────────────────────────────────────────────────"
echo "WARNING: This will overwrite the current (broken) state in S3."
echo "The broken state will still be accessible via S3 versioning."
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

cd "$ENV_DIR"

# Push the recovered state file back as the current state
terraform state push terraform.tfstate.recovered
echo "  ✓ Recovered state is now the current state in S3"
echo ""
echo "Press Enter to continue..."
read

# ── Step 4: Verify what Terraform sees now ──────────────────
echo "▶ STEP 4: Verify recovered state"
echo "──────────────────────────────────────────────────────"
echo "Resources Terraform now tracks (should match v1):"
terraform state list
echo ""

# ── Step 5: Plan to confirm no drift ────────────────────────
echo "▶ STEP 5: Run plan against your v1 code"
echo "──────────────────────────────────────────────────────"
echo "If recovery worked, plan should show:"
echo "  - Destroy: the bad resources added in v2"
echo "  - Update:  the changed resources back to v1 values"
echo ""
terraform plan
echo ""
echo "Press Enter to apply the rollback..."
read

# ── Step 6: Apply the rollback ──────────────────────────────
echo "▶ STEP 6: Apply rollback"
echo "──────────────────────────────────────────────────────"
terraform apply

echo ""
echo "✅ Recovery complete."
echo ""
echo "VERIFY in S3 — your state bucket now has:"
aws s3api list-object-versions \
  --bucket "$BUCKET" \
  --prefix "$STATE_KEY" \
  --region "$REGION" \
  --query 'Versions[*].{VersionId:VersionId,LastModified:LastModified,IsLatest:IsLatest}' \
  --output table
echo ""
echo "Notice: The broken v2 state is still there as an older version."
echo "S3 versioning never deletes — it's always recoverable."
