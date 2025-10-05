# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Accept build arguments from .env
ARG NEXT_PUBLIC_API_URL
ARG MONGODB_URI
ARG MONGODB_DB_NAME
ARG API_KEY_SECRET
ARG GEMINI_API_KEY
ARG ENVIRONMENT

# Set environment variables for build
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV MONGODB_URI=${MONGODB_URI}
ENV MONGODB_DB_NAME=${MONGODB_DB_NAME}
ENV API_KEY_SECRET=${API_KEY_SECRET}
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV ENVIRONMENT=${ENVIRONMENT}

# Disable telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application (skip linting)
RUN npm run build -- --no-lint || npm run build

# Stage 3: Runner (Production)
FROM node:20-alpine AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Accept runtime environment variables
ARG NEXT_PUBLIC_API_URL
ARG MONGODB_URI
ARG MONGODB_DB_NAME
ARG API_KEY_SECRET
ARG GEMINI_API_KEY
ARG ENVIRONMENT

# Set runtime environment variables
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV MONGODB_URI=${MONGODB_URI}
ENV MONGODB_DB_NAME=${MONGODB_DB_NAME}
ENV API_KEY_SECRET=${API_KEY_SECRET}
ENV GEMINI_API_KEY=${GEMINI_API_KEY}
ENV ENVIRONMENT=${ENVIRONMENT}

# Change ownership to nextjs user
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set port and hostname
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the application
CMD ["node", "server.js"]
