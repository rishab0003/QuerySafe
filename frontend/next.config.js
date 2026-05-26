/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // When running in Docker Compose the backend service is reachable
    // at the hostname 'backend'. Use that so the frontend can proxy
    // API requests to the backend container.
    return [
      { source: '/api/:path*', destination: 'http://backend:8000/:path*' },
    ];
  },
};
module.exports = nextConfig;
