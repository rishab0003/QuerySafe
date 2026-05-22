/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        jade: {
          DEFAULT: '#00C896',
          dim: '#00A87E',
          glow: 'rgba(0, 200, 150, 0.15)',
          subtle: 'rgba(0, 200, 150, 0.06)',
        },
        ink: {
          DEFAULT: '#06060C',
          950: '#08081A',
          900: '#0C0C1E',
          800: '#121228',
          700: '#1A1A38',
          600: '#252548',
          500: '#3A3A5C',
          400: '#606080',
          300: '#8888A8',
          200: '#B0B0C8',
          100: '#D0D0E0',
        },
        crimson: '#FF3B5C',
        amber: '#F5A623',
        blue: '#3B82F6',
        purple: '#8B5CF6',
      },
      fontFamily: {
        display: ['Syne', 'ui-sans-serif', 'system-ui'],
        body: ['DM Mono', 'ui-monospace', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular'],
      },
      boxShadow: {
        'jade-glow': '0 4px 24px rgba(0, 200, 150, 0.12)',
        'jade-glow-lg': '0 8px 40px rgba(0, 200, 150, 0.18)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.3), 0 1px 4px rgba(0, 0, 0, 0.2)',
        'elevated': '0 8px 40px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.3)',
        'inner-glow': 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-mesh': 'linear-gradient(135deg, var(--tw-gradient-stops))',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-right': 'slideInRight 0.35s ease-out',
        'pulse-glow': 'pulseGlow 2s infinite',
        'gradient-flow': 'gradientFlow 8s ease infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      borderRadius: {
        'xl': '16px',
        '2xl': '20px',
        '3xl': '24px',
      },
    },
  },
  plugins: [],
};
