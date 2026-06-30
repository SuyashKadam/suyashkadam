# Terraform Learning — Step-by-Step Execution Guide

Follow these steps in order. Each step builds on the last.

---

## Prerequisites

```bash
# Install Terraform (Mac)
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Install Terraform (Linux)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify
terraform version

# Install AWS CLI
pip install awscli
aws --version
```

---

## PHASE 1: AWS Setup (Do this in AWS Console)

### Step 1.1 — Create IAM user for Terraform (if you don't have one)

1. Go to AWS Console → IAM → Users → Create User
2. Name: `terraform-admin`
3. Attach policy: `AdministratorAccess` (for learning — restrict in real projects)
4. Create access keys → Download CSV

### Step 1.2 — Configure AWS CLI

```bash
aws configure
# AWS Access Key ID: paste from CSV
# AWS Secret Access Key: paste from CSV
# Default region: us-east-1
# Default output format: json

# Verify it works
aws sts get-caller-identity
# Should print your account ID and user ARN
```

### Step 1.3 — Create an EC2 Key Pair

1. AWS Console → EC2 → Key Pairs → Create Key Pair
2. Name: `my-dev-keypair`
3. Format: `.pem`
4. Download and move it:

```bash
mv ~/Downloads/my-dev-keypair.pem ~/.ssh/
chmod 400 ~/.ssh/my-dev-keypair.pem
```

### Step 1.4 — Get your public IP

```bash
curl ifconfig.me
# Note this IP — you'll put it in terraform.tfvars
```

---

## PHASE 2: Bootstrap (Run ONCE ever)

This creates the S3 bucket and DynamoDB table for state storage.

### Step 2.1 — Edit the bucket name

Open `bootstrap/variables.tf` and change:
```hcl
default = "yourname-terraform-state-2024"
# Change 'yourname' to something globally unique, like your name + AWS account last 4 digits
```

### Step 2.2 — Run bootstrap

```bash
cd terraform-learning/bootstrap

terraform init
# Downloads the AWS provider plugin

terraform plan
# Shows: will create S3 bucket + DynamoDB table

terraform apply
# Type 'yes' when prompted
# This takes ~30 seconds
```

### Step 2.3 — Verify in AWS Console

- S3 → should see your bucket with versioning enabled
- DynamoDB → should see `terraform-state-lock` table

> After this, never run terraform in the bootstrap folder again.

---

## PHASE 3: Update Backend Configs

Now update both environment backend files with your actual bucket name.

```bash
# In environments/dev/backend.tf — change this line:
bucket = "yourname-terraform-state-2024"  # use your actual bucket name

# In environments/prod/backend.tf — same bucket, different key
bucket = "yourname-terraform-state-2024"
```

---

## PHASE 4: Deploy Dev Environment

### Step 4.1 — Update terraform.tfvars

Open `environments/dev/terraform.tfvars`:
```hcl
key_name = "my-dev-keypair"   # The key pair you created
your_ip  = "1.2.3.4"          # Your actual IP from curl ifconfig.me
```

### Step 4.2 — Set the DB password as environment variable

```bash
# NEVER put this in a file
export TF_VAR_db_password="MySecurePass123!"
```

### Step 4.3 — Initialize dev

```bash
cd terraform-learning/environments/dev

terraform init
# Expected output:
# - Initializing backend... (connects to S3)
# - Initializing provider plugins... (downloads AWS provider)
# - Terraform has been successfully initialized!
```

**What just happened?**
- `.terraform/` folder was created with the downloaded provider
- A lock file `.terraform.lock.hcl` was created (commit this to git)
- Terraform connected to your S3 backend — state will be stored there

### Step 4.4 — Validate the code

```bash
terraform validate
# Should print: Success! The configuration is valid.
```

### Step 4.5 — Format check

```bash
terraform fmt -check -recursive
# If it exits 0: all files are properly formatted
# If it shows files: run terraform fmt to fix them
```

### Step 4.6 — Plan

```bash
terraform plan
```

Read the output carefully. You should see:
```
+ aws_vpc.main                    (will be created)
+ aws_subnet.public[0]           (will be created)
+ aws_subnet.public[1]           (will be created)
+ aws_subnet.private[0]          (will be created)
+ aws_subnet.private[1]          (will be created)
+ aws_internet_gateway.main      (will be created)
+ aws_route_table.public         (will be created)
...

Plan: 20 to add, 0 to change, 0 to destroy.
```

**Practice reading plans.** The `+` means create. `-` means destroy. `~` means update.

### Step 4.7 — Apply

```bash
terraform apply
# Review the plan one more time
# Type 'yes' and press Enter
```

This takes 5-10 minutes (RDS takes the longest).

### Step 4.8 — Check outputs

```bash
terraform output
# ec2_public_ip = "54.x.x.x"
# rds_endpoint  = "dev-mysql.xxxxx.us-east-1.rds.amazonaws.com:3306"
# vpc_id        = "vpc-xxxxxxxx"

# SSH to your EC2 instance
ssh -i ~/.ssh/my-dev-keypair.pem ec2-user@$(terraform output -raw ec2_public_ip)

# Visit in browser
curl http://$(terraform output -raw ec2_public_ip)
# Should see: Hello from dev environment
```

### Step 4.9 — Inspect the state file

```bash
# See all resources Terraform is tracking
terraform state list

# See details of a specific resource
terraform state show module.ec2.aws_instance.app

# See the raw state file (it's in S3, pull it locally to inspect)
terraform state pull | python3 -m json.tool | less
```

---

## PHASE 5: Practice State Operations

### Exercise 1: See what a change looks like

Edit `environments/dev/main.tf` — change instance type:
```hcl
# Change this:
instance_type = "t3.micro"
# To this:
instance_type = "t3.small"
```

Then run:
```bash
terraform plan
# You'll see:
# ~ aws_instance.app
#     instance_type: "t3.micro" -> "t3.small"
```

This is an in-place update (no downtime for instance type).

Revert the change and plan again to see it go back.

### Exercise 2: Force resource replacement

```bash
# This will DESTROY and RECREATE the EC2 instance
terraform plan -replace=module.ec2.aws_instance.app

# You'll see:
# -/+ aws_instance.app (forces replacement)
```

**Important:** `-/+` means downtime. Never do this on prod DB.

### Exercise 3: Remove from state without destroying

```bash
# Remove EC2 from Terraform's tracking (resource stays in AWS)
terraform state rm module.ec2.aws_instance.app

# Now run plan — Terraform will want to CREATE it again
terraform plan
# + aws_instance.app  (it thinks it doesn't exist)

# Import it back (get instance ID from AWS Console or CLI)
INSTANCE_ID=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=dev-app-server" --query "Reservations[0].Instances[0].InstanceId" --output text)
terraform import module.ec2.aws_instance.app $INSTANCE_ID

# Now plan again — no changes
terraform plan
```

### Exercise 4: Simulate state locking

```bash
# Terminal 1:
cd terraform-learning/environments/dev
terraform apply  # Don't type 'yes' yet, just let it run plan

# Terminal 2 (in same directory):
terraform plan
# You may see: Error: Error acquiring the state lock
# This is the DynamoDB lock working!
```

---

## PHASE 6: Cross-Environment Reference

Practice reading one environment's state from another.

Create a file `environments/dev/data.tf`:
```hcl
# Read the VPC ID from a separate "network" stack
# (In real projects, networking is often a separate Terraform root)
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "yourname-terraform-state-2024"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
  }
}

output "vpc_from_remote_state" {
  value = data.terraform_remote_state.network.outputs.vpc_id
}
```

```bash
terraform plan
terraform apply
terraform output vpc_from_remote_state
```

---

## PHASE 7: Deploy Prod (After dev works perfectly)

```bash
cd terraform-learning/environments/prod

# Set prod password (different from dev)
export TF_VAR_db_password="ProdSecurePass456!"

# Update terraform.tfvars with your IP and prod key pair name

terraform init
terraform plan -out=tfplan    # Save plan to file

# Review plan carefully — prod has:
# - 3 public subnets (not 2)
# - 3 private subnets
# - NAT Gateway (costs money!)
# - Multi-AZ RDS
# - deletion_protection = true on RDS

terraform apply tfplan          # Apply the saved plan exactly
```

---

## PHASE 8: Cleanup (Destroy Everything)

When done learning, destroy to avoid AWS charges.

```bash
# Destroy dev first
cd terraform-learning/environments/dev
terraform destroy
# Type 'yes'
# Takes 5-10 minutes

# Destroy prod
cd terraform-learning/environments/prod
# IMPORTANT: RDS has deletion_protection = true in prod
# You must disable it first:
# Go to terraform/modules/rds/main.tf → set deletion_protection = false
# terraform apply   (to remove protection)
# terraform destroy (now it will work)
```

**DO NOT destroy the bootstrap resources** — you'll need them for future practice.

---

## Common Errors and Fixes

### "Error: No valid credential sources found"
```bash
aws configure  # Re-enter your credentials
aws sts get-caller-identity  # Verify they work
```

### "Error acquiring the state lock"
Someone else (or a crashed previous run) holds the lock.
```bash
# Check who holds it
aws dynamodb get-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "yourname-terraform-state-2024/dev/terraform.tfstate"}}'

# If the process is dead, force unlock (use the LockID from above)
terraform force-unlock <LOCK_ID>
```

### "Error: Backend configuration changed"
```bash
terraform init -reconfigure
```

### "Resource already exists"
The resource exists in AWS but not in state. Import it:
```bash
terraform import <resource_address> <aws_resource_id>
```

### "Cycle: module.a depends on module.b depends on module.a"
You have a circular dependency. Use `depends_on` to break it or restructure outputs.

---

## Checklist: What You Can Now Do

- [ ] Explain what a state file is and why it needs to be remote
- [ ] Set up S3 backend with DynamoDB locking from scratch
- [ ] Explain the difference between dev and prod state files
- [ ] Read a `terraform plan` output and explain every symbol
- [ ] Run `terraform state list`, `show`, `rm`, `import`
- [ ] Explain why `terraform.tfvars` is committed but secrets aren't
- [ ] Set secrets via `TF_VAR_` environment variables
- [ ] Explain what DynamoDB locking prevents
- [ ] Explain `lifecycle { prevent_destroy = true }`
- [ ] Describe how CI/CD pipeline handles dev vs prod approval gates
