import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  eslint: {
    // 忽略ESLint错误，允许构建继续进行
    ignoreDuringBuilds: true,
  },
  typescript: {
    // 忽略TypeScript错误，允许构建继续进行
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
