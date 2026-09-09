/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: 'var(--navy-950)',
          900: 'var(--navy-900)',
          800: 'var(--navy-800)',
          700: 'var(--navy-700)',
          600: 'var(--navy-600)',
        },
        paper: 'var(--paper)',
        ink: 'var(--ink)',
        muted: {
          DEFAULT: 'var(--muted)',
          soft: 'var(--muted-soft)',
        },
        hairline: 'var(--hairline)',
        teal: {
          DEFAULT: 'var(--teal)',
          dark: 'var(--teal-dark)',
        },
        amber: {
          DEFAULT: 'var(--amber)',
          dark: 'var(--amber-dark)',
        },
        indigo: {
          DEFAULT: 'var(--indigo)',
        },
        rose: {
          DEFAULT: 'var(--rose)',
        },
        cat: {
          men: 'var(--men)',
          women: 'var(--women)',
          unisex: 'var(--unisex)',
          accessible: 'var(--accessible)',
        },
        pill: {
          bg: 'var(--pill-bg)',
          border: 'var(--pill-border)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        soft: 'var(--shadow-soft)',
        card: 'var(--shadow-card)',
      },
      borderRadius: {
        lg: 'var(--radius-lg)',
        md: 'var(--radius-md)',
        sm: 'var(--radius-sm)',
      }
    },
  },
  plugins: [],
}
