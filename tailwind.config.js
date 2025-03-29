/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./shop/templates/admin/**/*.html",  // Укажи путь к шаблонам админки, если кастомизируешь их
    "./static/admin/css/**/*.css",       // Для кастомных стилей
  ],
  theme: {
    extend: {
      colors: {
        'admin-bg': '#f9fafb',       // Светлый фон
        'admin-primary': '#1e3a8a',  // Тёмно-синий
        'admin-accent': '#3b82f6',   // Ярко-синий
        'admin-success': '#10b981',  // Зелёный
      },
    },
  },
  plugins: [],
}