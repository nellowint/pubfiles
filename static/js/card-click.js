// Delega clique do card-wrapper para o link interno
document.querySelectorAll('.card-wrapper').forEach(wrapper => {
    wrapper.addEventListener('click', (e) => {
        if (e.target.closest('a')) return;
        const link = wrapper.querySelector('a.card');
        if (link) link.click();
    });
});
