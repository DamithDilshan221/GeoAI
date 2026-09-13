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
        },
        pill: {
          bg: 'var(--pill-bg)',
          border: 'var(--pill-border)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'Outfit', 'Poppins', 'sans-serif'],
        outfit: ['Outfit', 'sans-serif'],
        jakarta: ['Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        soft: 'var(--shadow-soft)',
        card: 'var(--shadow-card)',
        'glass-specular': 'inset 0 1px 1.5px 0 rgba(255, 255, 255, 0.35), 0 12px 36px 0 rgba(0, 0, 0, 0.45)',
        'glass-pearl': 'inset 0 1.5px 2px rgba(255, 255, 255, 0.95), 0 12px 36px rgba(147, 112, 219, 0.15)',
        'glow-primary': '0 0 28px rgba(139, 92, 246, 0.55), inset 0 1px 2px rgba(255, 255, 255, 0.65)',
        'glow-teal': '0 0 24px rgba(45, 212, 191, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.5)',
      },
      borderRadius: {
        lg: 'var(--radius-lg)',
        md: 'var(--radius-md)',
        sm: 'var(--radius-sm)',
        '2xl': '20px',
        '3xl': '28px',
      }
    },
  },
  plugins: [],
}
