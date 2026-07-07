# ============================================================
# EXERCISE: State Recovery Practice
# Part 2 — v2 BROKEN Apply
#
# This simulates a bad deployment:
#   - app_config  → wrong port, wrong DB host (broke the app)
#   - nginx_config → someone deleted the health check endpoint
#   - env_file    → API_KEY wiped, wrong feature flags turned on
#     (imagine this took down your production service)
#
# Your job: roll back to v1 using the state file.
# ============================================================

terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

resource "local_file" "app_config" {
  filename = "${path.module}/output/app.conf"
  content  = <<-EOT
    # App Configuration — Version 2 (BROKEN)
    APP_NAME=myapp
    APP_PORT=9999          # WRONG PORT — app crashes on startup
    DB_HOST=wrong-host     # WRONG HOST — can't connect to DB
    DB_PORT=5432
    MAX_CONNECTIONS=10000  # Too high — connection pool exhausted
    CACHE_TTL=0            # Cache disabled — DB overloaded
    ENVIRONMENT=production
    DEPLOY_VERSION=2.0.0
  EOT
}

resource "local_file" "nginx_config" {
  filename = "${path.module}/output/nginx.conf"
  content  = <<-EOT
    server {
        listen 80;
        server_name myapp.com;

        location / {
            proxy_pass http://localhost:9999;  # Points to wrong port
        }

        # Health check REMOVED — load balancer now routes to dead instances
    }
  EOT
}

resource "local_file" "env_file" {
  filename = "${path.module}/output/.env"
  content  = <<-EOT
    NODE_ENV=production
    API_KEY=                         # BLANK — all API calls fail with 401
    FEATURE_FLAG_NEW_UI=true         # Untested UI shipped to prod
    FEATURE_FLAG_BETA_API=true       # Beta API not ready — crashes on use
    LOG_LEVEL=error                  # Reduced logging — harder to debug
  EOT
}

# This NEW resource is also problematic — references a path that doesn't exist
resource "local_file" "bad_new_resource" {
  filename = "${path.module}/output/database.conf"
  content  = <<-EOT
    # This was added by mistake in the same broken apply
    DB_REPLICA_HOST=does-not-exist
    DB_REPLICA_PORT=5433
  EOT
}
