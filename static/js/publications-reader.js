document.addEventListener('keydown', function(event) {
    if (event.key === "ArrowLeft") {
        const prevBtn = document.querySelector('.btn-cinema-prev:not(.disabled)');
        if(prevBtn) prevBtn.click();
    } else if (event.key === "ArrowRight" || event.key === " ") {
        const nextBtn = document.querySelector('.btn-cinema-next:not(.disabled)');
        if(nextBtn) nextBtn.click();
    } else if (event.key === "Escape") {
        document.querySelector('.btn-cinema-close').click();
    }
});
