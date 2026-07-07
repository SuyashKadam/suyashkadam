# Exercise: State File Versioning & Recovery

## What you will practice
1. Apply v1 — working state
2. Apply v2 — broken deployment (simulates production incident)
3. Inspect S3 versions of the state file
4. Restore the previous state version
5. Apply v1 code to bring everything back

---

## Part A — Local Practice (No AWS Needed)

This uses the `local` provider. Resources = files on your disk.
Fast, free, runs in under 2 minutes.

### Run it

```bash
# Terminal setup
cd terraform-learning/exercises/state-recovery

# ── APPLY V1 (the good state) ────────────────────────────
cd v1-initial
mkdir -p output
terraform init
terraform apply -auto-approve

# Inspect what was created
cat output/app.conf          # Should show PORT=8080, correct DB host
terraform state list         # See 3 resources tracked
terraform output             # Should show "v1.0.0 — stable"

# IMPORTANT: note the state file location
ls -la terraform.tfstate     # This is your v1 state

# ── APPLY V2 (the broken state) ──────────────────────────
cd ../v2-broken
mkdir -p output
terraform init
terraform apply -auto-approve

# Production is now "broken" — inspect the damage
cat output/app.conf          # Wrong port! Wrong DB host!
cat output/.env              # API_KEY is blank!
terraform state list         # Now shows 4 resources (bad_new_resource added)
terraform output             # Shows "BROKEN"

# ── RECOVERY ─────────────────────────────────────────────

# Step 1: See what the v1 state looks like
cat ../v1-initial/terraform.tfstate | python3 -m json.tool

# Step 2: Check the serial number (increments with each apply)
cat ../v1-initial/terraform.tfstate | python3 -m json.tool | grep serial
cat terraform.tfstate | python3 -m json.tool | grep serial
# v2 serial should be higher than v1

# Step 3: Copy v1 state into v2 directory
cp terraform.tfstate terraform.tfstate.v2-broken-backup
cp ../v1-initial/terraform.tfstate ./terraform.tfstate

# Step 4: Run plan — see what Terraform will do
# (v1 state + v2 code = Terraform sees the diff)
terraform plan
# You should see:
#   ~ update app_config (back to port 8080, correct host)
#   ~ update nginx_config (health check restored)
#   ~ update env_file (API_KEY restored)
#   - destroy bad_new_resource (wasn't in v1 state)

# Step 5: Apply the v1 code (go back to v1-initial directory)
cd ../v1-initial
terraform apply -auto-approve

# Step 6: Verify recovery
cat output/app.conf          # Should be back to PORT=8080
cat output/.env              # API_KEY restored
terraform state list         # Only 3 resources (bad_new_resource gone)
terraform output             # "v1.0.0 — stable"
```

---

## Part B — Real AWS S3 State Recovery

This is how you do it in production with remote state.

### The scenario
```
10:00  → terraform apply ran (v2 broken code merged by mistake)
10:02  → production alerts fire, app is down
10:05  → you need to roll back NOW
```

### Step-by-step commands

```bash
# ── 1. LIST all versions of your state file in S3 ────────
aws s3api list-object-versions \
  --bucket yourname-terraform-state-2024 \
  --prefix dev/terraform.tfstate \
  --query 'Versions[*].{VersionId:VersionId,LastModified:LastModified,IsLatest:IsLatest}' \
  --output table

# Output looks like:
# -----------------------------------------------------------------------
# |                      ListObjectVersions                             |
# +----------+-------------------------------+---------------------------+
# | IsLatest |        LastModified           |         VersionId         |
# +----------+-------------------------------+---------------------------+
# |  True    |  2024-01-15T10:02:33.000Z     |  KjH8s9Xm2...  ← BROKEN |
# |  False   |  2024-01-15T09:50:12.000Z     |  Abc1dEfG3...  ← GOOD ✓ |
# |  False   |  2024-01-14T15:22:08.000Z     |  Xyz9wVuT5...            |
# +----------+-------------------------------+---------------------------+

# ── 2. DOWNLOAD the good (previous) version ───────────────
aws s3api get-object \
  --bucket yourname-terraform-state-2024 \
  --key dev/terraform.tfstate \
  --version-id Abc1dEfG3...        # ← the good version ID
  terraform.tfstate.recovered

# ── 3. INSPECT the recovered state before pushing ────────
# Check what resources it tracks
cat terraform.tfstate.recovered | python3 -m json.tool | grep -E '"type"|"name"'

# Check the serial number (it must be lower than current)
cat terraform.tfstate.recovered | python3 -m json.tool | grep serial

# ── 4. PUSH the recovered state back ─────────────────────
cd environments/dev
terraform state push terraform.tfstate.recovered

# If serial is too low, terraform will refuse. Use -force carefully:
# terraform state push -force terraform.tfstate.recovered

# ── 5. VERIFY Terraform sees the restored state ───────────
terraform state list     # Should match v1 resources
terraform plan           # Should show: revert v2 changes

# ── 6. APPLY to make AWS match the recovered state ────────
terraform apply          # Reverts everything to v1
```

---

## What Each Command Does (for interview)

| Command | What it does |
|---|---|
| `aws s3api list-object-versions` | Lists every saved version of the state file — S3 keeps all of them because versioning is enabled |
| `aws s3api get-object --version-id` | Downloads a specific historical version of the state file |
| `terraform state push` | Uploads a local state file to the remote backend, making it the current state |
| `terraform state push -force` | Same but skips the serial number check (use carefully — means you're intentionally going back to an older state) |
| `terraform plan` after push | Shows what changes Terraform needs to make so AWS matches the recovered state |

---

## Key Things to Understand

**Why does S3 versioning save you?**
Every `terraform apply` writes a new version of the state file to S3.
S3 versioning keeps ALL previous versions — nothing is deleted.
This means you can go back to any point in time.

**What is the "serial" number?**
Inside every state file is a `"serial"` number that increments with each apply.
Terraform uses this to detect if you're trying to push an older state over a newer one.
It will refuse unless you use `-force` — this protects you from accidentally going backwards.

**The serial number in the state file:**
```json
{
  "version": 4,
  "terraform_version": "1.7.0",
  "serial": 12,          ← this increments every apply
  "lineage": "abc-123",  ← never changes — identifies this state's lineage
  "outputs": {},
  "resources": [...]
}
```

**Why not just re-apply v1 code without restoring state?**
If you just apply v1 code with the current (v2) state, Terraform will diff
v2 state against v1 code — it will try to fix things but may not get them
all right, especially if v2 added resources that v1 doesn't know about.
Restoring the state FIRST ensures Terraform works from a known good baseline.
