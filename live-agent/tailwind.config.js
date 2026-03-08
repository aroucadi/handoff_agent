/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'primary-purple': '#7b39fc',
                'primary-purple-hover': '#6a2ce0',
                'secondary-dark': '#2b2344',
                'secondary-dark-hover': '#352b54',
                'accent-orange': '#f87b52',
                'glass-border': 'rgba(164,132,215,0.5)',
                'glass-bg': 'rgba(85,80,110,0.4)',
            },
            fontFamily: {
                manrope: ['Manrope', 'sans-serif'],
                inter: ['Inter', 'sans-serif'],
                cabin: ['Cabin', 'sans-serif'],
                serif: ['Instrument Serif', 'serif'],
            },
            backdropBlur: {
                'xs': '2px',
            }
        },
    },
    plugins: [],
}
