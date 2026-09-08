// Alterna marcar/desmarcar todos os checkboxes DELETE do inline de páginas
(function() {
    'use strict';

    var LABEL_CHECK = 'Marcar todas para excluir';
    var LABEL_UNCHECK = 'Desmarcar todas';

    function findPagesGroup() {
        // acha o formset das páginas pelo TOTAL_FORMS (ex: pages-TOTAL_FORMS)
        var totals = document.querySelectorAll('input[name$="-TOTAL_FORMS"]');
        for (var i = 0; i < totals.length; i++) {
            var prefix = totals[i].name.replace(/-TOTAL_FORMS$/, '');
            var group = totals[i].closest('.inline-group') || totals[i].closest('fieldset') || document;
            var deletes = group.querySelectorAll('input[type="checkbox"][name^="' + prefix + '-"][name$="-DELETE"]');
            if (deletes.length > 0) {
                return { container: group, prefix: prefix, deletes: deletes };
            }
        }
        return null;
    }

    function allChecked(deletes) {
        for (var i = 0; i < deletes.length; i++) {
            if (!deletes[i].checked) return false;
        }
        return deletes.length > 0;
    }

    function refreshLabel(btn, deletes) {
        btn.textContent = allChecked(deletes) ? LABEL_UNCHECK : LABEL_CHECK;
    }

    function installButton(found) {
        var container = found.container;
        if (container.querySelector('.js-pages-bulk-toggle')) return;
        var header = container.querySelector('h2, h3, .inline-heading');
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn btn-sm btn-outline-danger js-pages-bulk-toggle';
        btn.style.marginLeft = '12px';
        refreshLabel(btn, found.deletes);
        btn.addEventListener('click', function() {
            var check = !allChecked(found.deletes);
            for (var i = 0; i < found.deletes.length; i++) {
                found.deletes[i].checked = check;
            }
            refreshLabel(btn, found.deletes);
        });
        if (header) {
            header.appendChild(btn);
        } else {
            container.insertBefore(btn, container.firstChild);
        }
        // mantém o rótulo sincronizado se o usuário marcar/desmarcar manualmente
        for (var j = 0; j < found.deletes.length; j++) {
            found.deletes[j].addEventListener('change', function() {
                refreshLabel(btn, found.deletes);
            });
        }
    }

    function init() {
        var found = findPagesGroup();
        if (!found) return;
        installButton(found);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
        window.addEventListener('load', init);
    } else {
        init();
    }
    // fallback para render tardio das tabs do Jazzmin
    setTimeout(init, 300);
    setTimeout(init, 800);
})();
