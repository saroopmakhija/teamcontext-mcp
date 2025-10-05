import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  
  // Only use standalone output for Docker builds
  ...(process.env.DOCKER_BUILD === 'true' && { output: 'standalone' }),
  
  eslint: {
    // Warning: Disabling ESLint during builds can lead to issues
    // Only ignore if necessary (e.g., during Docker builds)
    ignoreDuringBuilds: process.env.DOCKER_BUILD === 'true',
  },
  
  typescript: {
    // Warning: Disabling TypeScript checks can lead to runtime errors
    // Only ignore if necessary (e.g., during Docker builds)
    ignoreBuildErrors: process.env.DOCKER_BUILD === 'true',
  },
};

export default nextConfig;
