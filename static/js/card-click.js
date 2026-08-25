// Delega clique do card-wrapper para o link interno via delegação no grid
(function() {
    var grid = document.querySelector('.grid');
    if (!grid) return;
    grid.addEventListener('click', function(e) {
        var wrapper = e.target.closest('.card-wrapper');
        if (!wrapper) return;
        if (e.target.closest('a')) return;
        var link = wrapper.querySelector('a.card');
        if (link) link.click();
    });
})();
