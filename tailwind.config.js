/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/templates/**/*.html', // Scans all templates in all apps
    './**/static/js/**/*.js',    // If you use JS files that build HTML
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}