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

    // Re-executa scripts dentro de um container (necessário após clonagem)
    function reExecuteScripts(container) {
        var scripts = container.querySelectorAll('script');
        scripts.forEach(function(oldScript) {
            var newScript = document.createElement('script');
            // Copia atributos
            Array.from(oldScript.attributes).forEach(function(attr) {
                newScript.setAttribute(attr.name, attr.value);
            });
            // Copia conteúdo inline
            newScript.textContent = oldScript.textContent;
            // Substitui o script antigo pelo novo
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    }

    // Cards de anúncio na home — clona o card base baseado nas colunas do grid
    function initAdCards() {
        var adCard = document.getElementById('adCard');
        if (!adCard) return;

        var grid = adCard.parentElement;
        var pubCards = Array.from(grid.children).filter(function(el) {
            return !el.classList.contains('ad-card-wrapper');
        });

        if (pubCards.length < 2) {
            adCard.style.display = '';
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
        var adsToShow = columns;
        var adId = adCard.getAttribute('data-ad-id');

        // Posições aleatórias (evita início e fim)
        var minPos = 2;
        var maxPos = Math.max(minPos, pubCards.length - 1);

        // Função para trackear cliques
        function trackClick(card) {
            card.addEventListener('click', function(e) {
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

        // Remove clones existentes
        var existingClones = grid.querySelectorAll('.ad-card-wrapper:not(#adCard)');
        existingClones.forEach(function(clone) {
            clone.remove();
        });

        // Esconde o card original
        adCard.style.display = 'none';

        // Insere o card original
        var randomPos = Math.floor(Math.random() * (maxPos - minPos + 1)) + minPos;
        if (randomPos >= pubCards.length) {
            grid.appendChild(adCard);
        } else {
            grid.insertBefore(adCard, pubCards[randomPos]);
        }
        adCard.style.display = '';
        trackClick(adCard);

        // Clona o card para as posições restantes
        for (var i = 1; i < adsToShow; i++) {
            var clone = adCard.cloneNode(true);
            clone.id = 'adCard' + i;
            clone.style.display = 'none';

            randomPos = Math.floor(Math.random() * (maxPos - minPos + 1)) + minPos;
            if (randomPos >= pubCards.length) {
                grid.appendChild(clone);
            } else {
                grid.insertBefore(clone, pubCards[randomPos]);
            }
            clone.style.display = '';
            reExecuteScripts(clone);
            trackClick(clone);
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
