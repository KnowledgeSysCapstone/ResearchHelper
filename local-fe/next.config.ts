import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: {
    // Ignore ESLint errors, allow build to continue
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Ignore TypeScript errors, allow build to continue
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
