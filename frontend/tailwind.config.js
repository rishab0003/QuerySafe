module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        jade: '#00C896',
        ink: '#0A0A0F',
        'ink-800': '#121224',
        'ink-700': '#1e1e38',
        'ink-400': '#686888',
        crimson: '#FF3B5C',
        amber: '#F5A623'
      },
      fontFamily: {
        display: ['Syne', 'ui-sans-serif', 'system-ui'],
        body: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['DM Mono', 'ui-monospace', 'SFMono-Regular']
      },
      boxShadow: {
        'jade-glow': '0 6px 20px rgba(0,200,150,0.12)'
      }
    }
  },
  plugins: []
};
