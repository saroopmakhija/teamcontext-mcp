#!/bin/bash

# TeamContext Frontend Startup Script
echo "🎨 Starting TeamContext Frontend..."

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected to find: package.json"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local not found. Creating default configuration..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
    echo "✅ Created .env.local with default API URL"
fi

echo "🌐 Starting Next.js development server..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔧 Make sure your backend is running on: http://localhost:8000"
echo ""

npm run dev
