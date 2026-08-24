/* ============================================
   Advertisements — lógica dos anúncios
   ============================================ */

(function() {
    'use strict';

    // Carrossel de banners (home)
    function initCarousel() {
        var carousel = document.getElementById('adCarousel');
        if (!carousel) return;

        var track = carousel.querySelector('.ad-carousel-track');
        var slides = carousel.querySelectorAll('.ad-carousel-slide');
        var prevBtn = carousel.querySelector('.ad-carousel-prev');
        var nextBtn = carousel.querySelector('.ad-carousel-next');
        var dots = carousel.querySelectorAll('.ad-carousel-dot');

        if (slides.length <= 1) return;

        var current = 0;
        var total = slides.length;
        var autoPlayInterval = null;

        function goTo(index) {
            if (index < 0) index = total - 1;
            if (index >= total) index = 0;
            current = index;
            track.style.transform = 'translateX(-' + (current * 100) + '%)';
            dots.forEach(function(dot, i) {
                dot.classList.toggle('active', i === current);
            });
        }

        function startAutoPlay() {
            if (autoPlayInterval) clearInterval(autoPlayInterval);
            autoPlayInterval = setInterval(function() {
                goTo(current + 1);
            }, 4000);
        }

        function stopAutoPlay() {
            if (autoPlayInterval) {
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
            }
        }

        if (prevBtn) prevBtn.addEventListener('click', function() {
            goTo(current - 1);
            startAutoPlay();
        });

        if (nextBtn) nextBtn.addEventListener('click', function() {
            goTo(current + 1);
            startAutoPlay();
        });

        dots.forEach(function(dot, i) {
            dot.addEventListener('click', function() {
                goTo(i);
                startAutoPlay();
            });
        });

        carousel.addEventListener('mouseenter', stopAutoPlay);
        carousel.addEventListener('mouseleave', startAutoPlay);

        startAutoPlay();
    }

    // Card de anúncio na home — posição aleatória
    function initAdCard() {
        var adCard = document.getElementById('adCard');
        if (!adCard) return;

        var grid = adCard.parentElement;
        var cards = Array.from(grid.children).filter(function(el) {
            return el !== adCard;
        });

        if (cards.length < 2) {
            adCard.style.display = '';
            return;
        }

        // Posição aleatória entre 2 e N-1 (não fica nem no início nem no fim)
        var minPos = 2;
        var maxPos = Math.max(minPos, cards.length - 1);
        var randomPos = Math.floor(Math.random() * (maxPos - minPos + 1)) + minPos;

        if (randomPos >= cards.length) {
            grid.appendChild(adCard);
        } else {
            grid.insertBefore(adCard, cards[randomPos]);
        }

        adCard.style.display = '';

        // Trackear cliques no card para incrementar contador de views
        adCard.addEventListener('click', function(e) {
            var adId = adCard.getAttribute('data-ad-id');
            if (!adId) return;

            // Incrementa contador em background
            fetch('/advertisements/click/' + adId + '/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/json'
                },
                keepalive: true
            });
        });
    }

    // Popup de preview no reader
    function initPreviewPopup() {
        var popup = document.getElementById('adPreviewPopup');
        if (!popup) return;

        var closeBtn = document.getElementById('adPreviewClose');
        var content = document.getElementById('adPreviewContent');
        var adItems = content.querySelectorAll('.ad-preview-item');

        if (adItems.length === 0) {
            popup.style.display = 'none';
            return;
        }

        var currentIndex = 0;

        function showAd() {
            adItems.forEach(function(item, index) {
                item.style.display = (index === currentIndex) ? '' : 'none';
            });
        }

        function nextAd() {
            currentIndex = (currentIndex + 1) % adItems.length;
            showAd();
        }

        // Mostra primeiro anúncio
        showAd();

        // Fecha popup
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                popup.style.display = 'none';
            });
        }

        // Troca anúncio ao navegar (observa mudanças na URL do reader)
        var lastPage = window.location.pathname;
        var observer = new MutationObserver(function() {
            var currentPage = window.location.pathname;
            if (currentPage !== lastPage) {
                lastPage = currentPage;
                if (popup.style.display !== 'none') {
                    nextAd();
                }
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Inicializa tudo
    document.addEventListener('DOMContentLoaded', function() {
        initCarousel();
        initAdCard();
        initPreviewPopup();
    });
})();
