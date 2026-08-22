// Torna as linhas da tabela do admin clicáveis
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        var rows = document.querySelectorAll('#result_list tbody tr');

        rows.forEach(function(row) {
            var link = row.querySelector('th a, td a');
            if (link) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function(e) {
                    // Não navegar se clicou em um link, checkbox ou botão
                    if (e.target.tagName === 'A' || e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
                        return;
                    }
                    window.location = link.href;
                });
            }
        });
    });
})();
