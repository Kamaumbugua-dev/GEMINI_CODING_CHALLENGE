#!/bin/bash
# =============================================================================
# Voice UI Navigator — Automated Cloud Deployment Script
# =============================================================================
# This script automates the full deployment pipeline to Google Cloud Run:
#   1. Validates required environment variables
#   2. Enables required GCP APIs
#   3. Creates Artifact Registry repository (if not exists)
#   4. Grants required IAM permissions
#   5. Builds and pushes Docker image via Cloud Build
#   6. Deploys to Cloud Run
# =============================================================================

set -e  # Exit immediately on any error

# ── Configuration ─────────────────────────────────────────────────────────────
PROJECT_ID="project-0b604228-c127-4a86-bdb"
REGION="us-central1"
SERVICE_NAME="voice-navigator"
REPO_NAME="voice-navigator-repo"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME"

# ── Colour output ─────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log()  { echo -e "${GREEN}[✔] $1${NC}"; }
warn() { echo -e "${YELLOW}[!] $1${NC}"; }
fail() { echo -e "${RED}[✘] $1${NC}"; exit 1; }

echo ""
echo "=============================================="
echo "  Voice UI Navigator — Cloud Deployment"
echo "=============================================="
echo ""

# ── Step 1: Validate GEMINI_API_KEY ───────────────────────────────────────────
if [ -z "$GEMINI_API_KEY" ]; then
    # Try loading from .env file
    if [ -f "app/.env" ]; then
        export $(grep -v '^#' app/.env | xargs)
    fi
fi

if [ -z "$GEMINI_API_KEY" ]; then
    fail "GEMINI_API_KEY is not set. Export it or add it to app/.env before deploying."
fi
log "GEMINI_API_KEY found"

# ── Step 2: Set GCP project ───────────────────────────────────────────────────
gcloud config set project "$PROJECT_ID" --quiet
log "GCP project set to $PROJECT_ID"

# ── Step 3: Enable required APIs ─────────────────────────────────────────────
log "Enabling required GCP APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    --quiet
log "APIs enabled"

# ── Step 4: Get project number for IAM bindings ───────────────────────────────
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
log "Project number: $PROJECT_NUMBER"

# ── Step 5: Create Artifact Registry repo (skip if exists) ───────────────────
if gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --quiet 2>/dev/null; then
    warn "Artifact Registry repo '$REPO_NAME' already exists — skipping creation"
else
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Voice Navigator container images" \
        --quiet
    log "Artifact Registry repo created"
fi

# ── Step 6: Grant IAM permissions ─────────────────────────────────────────────
log "Granting IAM permissions to Cloud Build service accounts..."

gcloud artifacts repositories add-iam-policy-binding "$REPO_NAME" \
    --location="$REGION" \
    --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
    --role="roles/artifactregistry.writer" \
    --quiet

gcloud artifacts repositories add-iam-policy-binding "$REPO_NAME" \
    --location="$REGION" \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/artifactregistry.writer" \
    --quiet

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/logging.logWriter" \
    --quiet

log "IAM permissions granted"

# ── Step 7: Build and push Docker image ───────────────────────────────────────
log "Building and pushing Docker image via Cloud Build..."
gcloud builds submit --tag "$IMAGE" --quiet
log "Docker image pushed: $IMAGE"

# ── Step 8: Deploy to Cloud Run ───────────────────────────────────────────────
log "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,GOOGLE_GENAI_USE_VERTEXAI=False" \
    --quiet

# ── Done ──────────────────────────────────────────────────────────────────────
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format="value(status.url)")

echo ""
echo "=============================================="
log "Deployment complete!"
echo -e "  ${GREEN}Service URL: $SERVICE_URL${NC}"
echo "=============================================="
echo ""
