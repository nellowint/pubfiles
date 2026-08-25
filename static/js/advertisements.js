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

    // Cards de anúncio na home — insere cards baseado nas colunas do grid
    function initAdCards() {
        var adCards = Array.from(document.querySelectorAll('.ad-card-wrapper'));
        if (adCards.length === 0) return;

        var grid = adCards[0].parentElement;
        var pubCards = Array.from(grid.children).filter(function(el) {
            return !el.classList.contains('ad-card-wrapper');
        });

        if (pubCards.length < 2) {
            adCards.forEach(function(card) { card.style.display = ''; });
            return;
        }

        // Calcula número de colunas baseado na largura do grid
        var gridWidth = grid.offsetWidth;
        var columns;
        if (gridWidth >= 1200) {
            columns = 5;
        } else if (gridWidth >= 900) {
            columns = 4;
        } else if (gridWidth >= 600) {
            columns = 3;
        } else {
            columns = 2;
        }

        // Quantidade de cards de anúncio baseada nas colunas
        var adsToShow;
        if (columns === 3) {
            adsToShow = 1;
        } else {
            adsToShow = columns;
        }
        adsToShow = Math.min(adsToShow, adCards.length);

        // Posições aleatórias (evita início e fim)
        var minPos = 2;
        var maxPos = Math.max(minPos, pubCards.length - 1);

        // Função para trackear cliques
        function trackClick(card) {
            card.addEventListener('click', function(e) {
                var adId = card.getAttribute('data-ad-id');
                if (!adId) return;
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

        // Esconde todos primeiro
        adCards.forEach(function(card) {
            card.style.display = 'none';
        });

        // Insere os cards que serão mostrados
        for (var i = 0; i < adsToShow; i++) {
            var adCard = adCards[i];
            var randomPos = Math.floor(Math.random() * (maxPos - minPos + 1)) + minPos;

            if (randomPos >= pubCards.length) {
                grid.appendChild(adCard);
            } else {
                grid.insertBefore(adCard, pubCards[randomPos]);
            }
            adCard.style.display = '';
            trackClick(adCard);
        }
    }

    // Debounce para resize
    var resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            initAdCards();
        }, 250);
    });

    // Inicializa tudo
    document.addEventListener('DOMContentLoaded', function() {
        initCarousel();
        initAdCards();
    });
})();
