# Frontend Docker Deployment Guide

Complete Docker setup for the TeamContext frontend using environment variables from the root `.env` file.

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Root `.env` file configured at `/teamcontext-mcp/.env`

## Environment Variables

The Docker setup uses environment variables from the **root `.env` file** (`/teamcontext-mcp/.env`):

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=teamcontext
API_KEY_SECRET=hackathon-demo-key-2025
GEMINI_API_KEY=your-gemini-api-key
ENVIRONMENT=development
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Quick Start

### Build and Run with Docker Compose

From the **frontend directory**:

```bash
cd frontend
docker-compose up --build
```

The app will be available at: **http://localhost:3000**

### Run in Detached Mode

```bash
docker-compose up -d --build
```

### Stop the Container

```bash
docker-compose down
```

## Manual Docker Commands

### Build the Image

```bash
cd frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 \
  --build-arg MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net \
  --build-arg MONGODB_DB_NAME=teamcontext \
  --build-arg API_KEY_SECRET=your-secret \
  --build-arg GEMINI_API_KEY=your-key \
  --build-arg ENVIRONMENT=production \
  -t teamcontext-frontend .
```

### Run the Container

```bash
docker run -d \
  -p 3000:3000 \
  --env-file ../.env \
  --name teamcontext-frontend \
  --restart unless-stopped \
  teamcontext-frontend
```

## Production Deployment

For production, update the root `.env` file with production values:

```env
MONGODB_URI=mongodb+srv://prod_user:prod_pass@prod-cluster.mongodb.net
MONGODB_DB_NAME=teamcontext_prod
API_KEY_SECRET=strong-production-secret
GEMINI_API_KEY=production-gemini-key
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
```

Then build and deploy:

```bash
cd frontend
docker-compose up -d --build
```

## Docker Build Features

### Multi-Stage Build

The Dockerfile uses a 3-stage build:
1. **deps**: Installs Node.js dependencies
2. **builder**: Builds the Next.js application with environment variables
3. **runner**: Minimal production runtime (~200MB)

### Security

- Runs as non-root user (`nextjs`)
- Minimal Alpine Linux base image
- No development dependencies in production

### Environment Variables

All environment variables from root `.env` are:
- Passed as build arguments
- Available during build time
- Available at runtime
- Automatically loaded via `env_file` in docker-compose

## Common Commands

```bash
# View logs
docker-compose logs -f

# View logs (last 100 lines)
docker-compose logs --tail=100 -f

# Restart container
docker-compose restart

# Rebuild without cache
docker-compose build --no-cache

# Stop and remove containers
docker-compose down

# Stop, remove containers and volumes
docker-compose down -v

# Execute command in container
docker-compose exec frontend sh

# Check container status
docker-compose ps
```

## Troubleshooting

### Build Fails with Linting Errors

Linting is disabled in the Dockerfile with:
```dockerfile
ENV ESLINT_NO_DEV_ERRORS=true
ENV NEXT_TELEMETRY_DISABLED=1
```

If still failing, check the build logs:
```bash
docker-compose logs --tail=50
```

### Can't Connect to Backend

Check `NEXT_PUBLIC_API_URL` in root `.env`:
- For local development: `http://localhost:8000/api/v1`
- For Docker networking: `http://backend:8000/api/v1`
- For production: `https://api.yourdomain.com/api/v1`

### Environment Variables Not Loading

Ensure:
1. Root `.env` file exists at `/teamcontext-mcp/.env`
2. `docker-compose.yml` has `env_file: - ../.env`
3. Rebuild after changing `.env`: `docker-compose up --build`

### Port 3000 Already in Use

Change the host port in `docker-compose.yml`:
```yaml
ports:
  - "4000:3000"  # Access on http://localhost:4000
```

### Container Won't Start

Check logs:
```bash
docker-compose logs frontend
```

Common issues:
- Missing `.env` file
- Invalid environment variable values
- Port conflicts

## Health Checks

### Check if Frontend is Running

```bash
curl http://localhost:3000
```

Expected: HTML response with Next.js content

### Check Environment Variables Inside Container

```bash
docker-compose exec frontend sh -c "env | grep NEXT_PUBLIC"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Create .env file
        run: |
          echo "NEXT_PUBLIC_API_URL=${{ secrets.API_URL }}" >> .env
          echo "MONGODB_URI=${{ secrets.MONGODB_URI }}" >> .env
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> .env
      
      - name: Build Docker image
        run: |
          cd frontend
          docker-compose build
      
      - name: Deploy
        run: |
          docker-compose up -d
```

## Performance Tips

### Build Cache

Docker caches layers. To maximize cache hits:
- Dependencies are copied and installed first
- Application code is copied after
- This means code changes don't require reinstalling dependencies

### Image Size

Final image is optimized to ~200MB:
- Alpine Linux base
- Multi-stage build removes build tools
- Only production dependencies
- Standalone Next.js output

## Security Best Practices

⚠️ **Important:**
- Never commit `.env` files to git
- Use `.env.example` for templates
- Rotate secrets regularly
- Use strong passwords for MongoDB
- Restrict CORS in production
- Enable HTTPS in production

## Support

For issues:
1. Check logs: `docker-compose logs frontend`
2. Verify `.env` file exists and has correct values
3. Ensure Docker daemon is running
4. Try rebuilding without cache: `docker-compose build --no-cache`
