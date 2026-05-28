/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // When running in Docker Compose the backend service is reachable
    // at the hostname 'backend'. Use that so the frontend can proxy
    // API requests to the backend container.
    // Strip trailing '/api' from NEXT_PUBLIC_API_URL if present to align with backend routing
    const apiTarget = (process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000').replace(/\/api$/, '');
    return [
      { source: '/api/:path*', destination: `${apiTarget}/:path*` },
    ];
  },
};
module.exports = nextConfig;

