#!/usr/bin/env bash
# ============================================================
# LOCAL STATE RECOVERY SCRIPT
# Run this after the broken v2 apply to roll back to v1.
# ============================================================
set -e

EXERCISE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
V1_DIR="$EXERCISE_DIR/v1-initial"
V2_DIR="$EXERCISE_DIR/v2-broken"

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         TERRAFORM STATE RECOVERY — LOCAL             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Show current broken state ───────────────────────
echo "▶ STEP 1: Current state of broken v2 deployment"
echo "──────────────────────────────────────────────────────"
echo "Contents of broken app.conf:"
cat "$V2_DIR/output/app.conf" 2>/dev/null || echo "(file not found)"
echo ""
echo "Press Enter to continue..."
read

# ── Step 2: Show state versions ─────────────────────────────
echo "▶ STEP 2: List available state file versions"
echo "──────────────────────────────────────────────────────"
echo "In S3 remote state, you would run:"
echo ""
echo "  aws s3api list-object-versions \\"
echo "    --bucket yourname-terraform-state-2024 \\"
echo "    --prefix dev/terraform.tfstate \\"
echo "    --query 'Versions[*].{VersionId:VersionId,LastModified:LastModified}'"
echo ""
echo "For this LOCAL exercise, we have these backups:"
ls -la "$V1_DIR/terraform.tfstate.backup" 2>/dev/null && \
  echo "  → v1-initial/terraform.tfstate.backup (v1 — the good state)" || \
  echo "  → Run the exercise first: cd v1-initial && terraform apply"
echo ""
echo "Press Enter to continue..."
read

# ── Step 3: Copy v1 state over v2 ───────────────────────────
echo "▶ STEP 3: Restore v1 state file"
echo "──────────────────────────────────────────────────────"

if [ ! -f "$V1_DIR/terraform.tfstate" ]; then
  echo "ERROR: v1 state not found. Run v1-initial apply first."
  exit 1
fi

# Back up the broken v2 state before overwriting
cp "$V2_DIR/terraform.tfstate" "$V2_DIR/terraform.tfstate.broken-backup" 2>/dev/null || true
echo "  ✓ Backed up broken v2 state to terraform.tfstate.broken-backup"

# Copy the v1 state into v2 directory
cp "$V1_DIR/terraform.tfstate" "$V2_DIR/terraform.tfstate"
echo "  ✓ Restored v1 state into v2-broken directory"
echo ""
echo "Press Enter to continue..."
read

# ── Step 4: Plan with v1 state + v2 code ────────────────────
echo "▶ STEP 4: Run terraform plan (state=v1, code=v2)"
echo "──────────────────────────────────────────────────────"
echo "Watch what Terraform wants to do:"
echo "  - Resources in v1 state but NOT in v2 code → destroy"
echo "  - Resources in v2 code but NOT in v1 state → create"
echo "  - Changed resources → update"
echo ""
cd "$V2_DIR"
terraform plan
echo ""
echo "Press Enter to continue..."
read

# ── Step 5: Revert to v1 code ───────────────────────────────
echo "▶ STEP 5: Apply v1 code with restored state"
echo "──────────────────────────────────────────────────────"
echo "Now apply the v1 code (with the restored v1 state)."
echo "Terraform will:"
echo "  - Destroy bad_new_resource (was in v2 code, not in v1 state)"
echo "  - Update the 3 files back to their v1 content"
echo ""
cd "$V1_DIR"
terraform apply
echo ""

# ── Step 6: Verify recovery ─────────────────────────────────
echo "▶ STEP 6: Verify — check recovered files"
echo "──────────────────────────────────────────────────────"
echo "app.conf is now:"
cat "$V1_DIR/output/app.conf"
echo ""
echo "✅ Recovery complete. Production is back to v1."
