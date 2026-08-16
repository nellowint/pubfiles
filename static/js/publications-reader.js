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

// Reels functionality (Mobile)
(function() {
    const reelsWrapper = document.querySelector('.reels-wrapper');
    if (!reelsWrapper) return;

    const currentPage = parseInt(reelsWrapper.dataset.currentPage);
    const totalPages = parseInt(reelsWrapper.dataset.totalPages);
    const slug = reelsWrapper.dataset.slug;
    const counter = document.querySelector('.reels-counter');
    const currentSpan = counter ? counter.querySelector('.reels-current') : null;

    // Scroll to current page on load
    const currentReel = document.querySelector(`.reel-page[data-page-number="${currentPage}"]`);
    if (currentReel) {
        reelsWrapper.scrollTop = currentReel.offsetTop;
    }

    // Update counter and progress on scroll
    let scrollTimeout;
    reelsWrapper.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            const scrollTop = reelsWrapper.scrollTop;
            const viewportHeight = window.innerHeight;
            const pages = document.querySelectorAll('.reel-page');
            
            let activePage = 1;
            pages.forEach(function(page, index) {
                const pageTop = page.offsetTop;
                const pageBottom = pageTop + page.offsetHeight;
                
                if (scrollTop >= pageTop - viewportHeight / 2 && scrollTop < pageBottom - viewportHeight / 2) {
                    activePage = index + 1;
                }
            });

            // Update counter
            if (currentSpan) {
                currentSpan.textContent = activePage;
            }

            // Navigate to new page URL if different from current
            if (activePage !== currentPage) {
                const newUrl = `/publication/${slug}/read/page/${activePage}/`;
                history.replaceState(null, '', newUrl);
            }
        }, 100);
    });

    // Double tap to like (placeholder for future feature)
    let lastTap = 0;
    reelsWrapper.addEventListener('touchend', function(e) {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTap;
        
        if (tapLength < 500 && tapLength > 0) {
            // Double tap detected - could add like animation here
            e.preventDefault();
        }
        
        lastTap = currentTime;
    });
})();
