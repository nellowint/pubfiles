// Esconde posição quando tipo é SOCIALBAR (não depende de posição)
document.addEventListener('DOMContentLoaded', function() {
    var typeSelect = document.getElementById('id_type');
    var positionRow = document.getElementById('id_position') ? document.getElementById('id_position').closest('.form-row') : null;
    // fallback para Jazzmin: procura pelo label
    if (!positionRow) {
        var posLabel = document.querySelector('label[for="id_position"]');
        if (posLabel) positionRow = posLabel.closest('.form-row') || posLabel.closest('.field-position');
    }
    function togglePosition() {
        if (!typeSelect || !positionRow) return;
        var positionSelect = document.getElementById('id_position');
        if (typeSelect.value === 'social_bar') {
            positionRow.style.display = 'none';
            if (positionSelect) {
                positionSelect.value = '';
                positionSelect.disabled = true;
                positionSelect.removeAttribute('required');
            }
        } else {
            positionRow.style.display = '';
            if (positionSelect) {
                positionSelect.disabled = false;
            }
        }
    }
    if (typeSelect) {
        typeSelect.addEventListener('change', togglePosition);
        togglePosition();
    }
});
