// admin/js/my_custom_admin.js
(function($) {
    $(document).ready(function() {
        // Предпросмотр изображения при загрузке
        $('input[type="file"][name="image"]').on('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = $('<img>').attr('src', e.target.result).css({
                        'max-height': '100px',
                        'margin-top': '10px'
                    });
                    $(e.target).after(preview);
                };
                reader.readAsDataURL(file);
            }
        });

        // Подсветка строк с низким запасом
        $('td.field-stock').each(function() {
            const stock = parseInt($(this).text());
            if (stock < 5) {
                $(this).closest('tr').addClass('admin-row-low-stock');
            }
        });

        // Подтверждение перед массовыми действиями
        $('select[name="action"]').on('change', function() {
            const action = $(this).val();
            if (action && action.includes('delete') || action.includes('cancel')) {
                return confirm('Вы уверены, что хотите выполнить это действие?');
            }
        });
    });
})(django.jQuery);