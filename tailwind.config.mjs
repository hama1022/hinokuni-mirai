/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#fff4ed',
          100: '#ffe6d5',
          200: '#fecbaa',
          300: '#fda474',
          400: '#fb743c',
          500: '#f95016',
          600: '#e8380c',
          700: '#c1280c',
          800: '#9a2212',
          900: '#7c1f12',
        },
      },
      fontFamily: {
        sans: ['"Noto Sans JP"', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
