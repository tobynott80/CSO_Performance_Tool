/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "app/templates/index.html"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@preline/plugin'),
    require('@tailwindcss/forms')
  ],
}

