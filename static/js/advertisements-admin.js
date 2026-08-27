// Esconde posição quando tipo é SOCIALBAR ou SMARTLINK (não dependem de posição)
(function() {
    function findPositionRow() {
        var outer = document.querySelector('.form-group.field-position');
        if (outer) return outer;
        var el = document.getElementById('id_position');
        if (!el) return null;
        var g = el.closest('.form-group');
        if (g) return g;
        return el.closest('.form-row') || el.parentElement?.parentElement || el.parentElement;
    }
    function findTypeSelect() {
        return document.getElementById('id_type');
    }
    function getTypeValue(typeSelect) {
        var val = typeSelect.value;
        if (val) return val;
        // fallback para select2/jQuery quando value ainda não sincronizou
        try {
            if (window.jQuery) {
                var jv = window.jQuery('#id_type').val();
                if (jv) return jv;
            }
            if (window.django && window.django.jQuery) {
                var djv = window.django.jQuery('#id_type').val();
                if (djv) return djv;
            }
        } catch (e) {}
        return val;
    }
    function findPositionSelect2() {
        // container do select2 específico da posição
        var c = document.getElementById('select2-id_position-container');
        if (c) {
            var s2 = c.closest('.select2-container');
            if (s2) return s2;
        }
        // fallback: span select2 irmão do select
        var sel = document.getElementById('id_position');
        if (sel && sel.nextElementSibling && sel.nextElementSibling.classList.contains('select2')) {
            return sel.nextElementSibling;
        }
        return null;
    }
    function togglePosition() {
        var typeSelect = findTypeSelect();
        var positionRow = findPositionRow();
        var positionSelect = document.getElementById('id_position');
        if (!typeSelect || !positionRow) return;
        var val = getTypeValue(typeSelect);
        var hide = (val === 'social_bar' || val === 'smart_link');
        var s2 = findPositionSelect2();
        if (hide) {
            positionRow.style.display = 'none';
            if (positionSelect) {
                positionSelect.value = '';
                positionSelect.disabled = true;
                positionSelect.removeAttribute('required');
                // notifica select2 para limpar seleção visual
                try {
                    if (window.jQuery) window.jQuery('#id_position').val('').trigger('change.select2');
                    if (window.django && window.django.jQuery) window.django.jQuery('#id_position').val('').trigger('change.select2');
                } catch (e) {}
            }
            if (s2) s2.style.display = 'none';
        } else {
            positionRow.style.display = '';
            if (positionSelect) {
                positionSelect.disabled = false;
            }
            if (s2) s2.style.display = '';
            // garante que container genérico dentro da linha também volte
            var innerS2 = positionRow.querySelector('.select2-container');
            if (innerS2) innerS2.style.display = '';
        }
    }
    function init() {
        var typeSelect = findTypeSelect();
        if (!typeSelect) return;
        typeSelect.addEventListener('change', togglePosition);
        // jazzmin usa select2 que dispara change via jquery + eventos select2
        try {
            if (window.django && window.django.jQuery) {
                window.django.jQuery('#id_type').on('change', togglePosition);
                window.django.jQuery('#id_type').on('select2:select select2:unselect', togglePosition);
            }
            if (window.jQuery) {
                window.jQuery('#id_type').on('change', togglePosition);
                window.jQuery('#id_type').on('select2:select select2:unselect', togglePosition);
            }
        } catch (e) {}
        togglePosition();
        setTimeout(togglePosition, 300);
        setTimeout(togglePosition, 800);
        setTimeout(togglePosition, 1500);
        // observer para quando jazzmin re-renderiza abas
        try {
            var obs = new MutationObserver(togglePosition);
            obs.observe(document.body, { childList: true, subtree: true });
            setTimeout(function() { obs.disconnect(); }, 5000);
        } catch (e) {}
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
        window.addEventListener('load', init);
    } else {
        init();
    }
})();
