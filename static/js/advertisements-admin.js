// Esconde posição quando tipo é SOCIALBAR ou SMARTLINK (não dependem de posição)
(function() {
    function findPositionRow() {
        // Jazzmin tem 2 elementos .field-position: outer form-group e inner col; precisamos do outer que contém o label
        var outer = document.querySelector('.form-group.field-position');
        if (outer) return outer;
        var el = document.getElementById('id_position');
        if (!el) return null;
        // fallback: sobe até achar form-group
        var g = el.closest('.form-group');
        if (g) return g;
        return el.closest('.form-row') || el.parentElement?.parentElement || el.parentElement;
    }
    function findTypeSelect() {
        return document.getElementById('id_type');
    }
    function togglePosition() {
        var typeSelect = findTypeSelect();
        var positionRow = findPositionRow();
        var positionSelect = document.getElementById('id_position');
        if (!typeSelect || !positionRow) return;
        if (typeSelect.value === 'social_bar' || typeSelect.value === 'smart_link') {
            positionRow.style.display = 'none';
            if (positionSelect) {
                positionSelect.value = '';
                positionSelect.disabled = true;
                positionSelect.removeAttribute('required');
                // esconde select2 container se existir
                var s2 = document.querySelector('[aria-labelledby="select2-id_position-container"]')?.closest('.form-group') || document.querySelector('.select2-container');
                if (s2 && s2.closest('.field-position') === positionRow) s2.style.display = 'none';
            }
        } else {
            positionRow.style.display = '';
            if (positionSelect) {
                positionSelect.disabled = false;
            }
            var s2 = document.querySelector('.select2-container');
            if (s2) s2.style.display = '';
        }
    }
    function init() {
        var typeSelect = findTypeSelect();
        if (!typeSelect) return;
        typeSelect.addEventListener('change', togglePosition);
        // jazzmin usa select2 que dispara change via jquery
        if (window.django && window.django.jQuery) {
            window.django.jQuery('#id_type').on('change', togglePosition);
        }
        if (window.jQuery) {
            window.jQuery('#id_type').on('change', togglePosition);
        }
        togglePosition();
        // fallback para quando jazzmin renderiza via tabs/ajax
        setTimeout(togglePosition, 300);
        setTimeout(togglePosition, 800);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
        window.addEventListener('load', init);
    } else {
        init();
    }
})();
