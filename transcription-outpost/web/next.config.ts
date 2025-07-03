/** @type {import('next').NextConfig} */
const nextConfig = {
  // Change build directory to avoid permission issues
  distDir: '.next-build',
  // Disable source maps in development to reduce file I/O
  productionBrowserSourceMaps: false,
  // Disable experimental optimizations
  experimental: {
    // @ts-ignore
    disableOptimizedLoading: true,
  },
}

// Disable telemetry completely
process.env.NEXT_TELEMETRY_DISABLED = '1'

module.exports = nextConfig
