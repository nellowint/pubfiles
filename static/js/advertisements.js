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

    function createAdIframe(scriptHtml, container, adId) {
        var iframe = document.createElement('iframe');
        iframe.style.cssText = 'width:100%;height:100%;border:none;display:block;min-height:250px;';
        iframe.setAttribute('scrolling', 'no');
        iframe.setAttribute('frameborder', '0');
        if (adId) iframe.dataset.adId = adId;
        var doc = '<!DOCTYPE html><html><head><meta charset=\"utf-8\"><style>html,body{margin:0;padding:0;background:transparent;display:flex;align-items:center;justify-content:center;min-height:100%;}</style></head><body>' + scriptHtml + '</body></html>';
        iframe.srcdoc = doc;
        container.innerHTML = '';
        container.appendChild(iframe);

        // Polling via rAF: detecta clique dentro do iframe same-origin (srcdoc) via activeElement
        // Conta a cada vez que o iframe ganha foco (cada clique)
        (function pollIframeFocus() {
            var wasFocused = false;
            function check() {
                var isFocused = document.activeElement === iframe;
                if (isFocused && !wasFocused) {
                    wasFocused = true;
                    var wrapper = iframe.closest('.ad-card-wrapper');
                    if (wrapper) {
                        var id = iframe.dataset.adId;
                        var tokenEl = document.querySelector('[name=csrfmiddlewaretoken]');
                        if (id && tokenEl) {
                            fetch('/advertisements/click/' + id + '/', {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': tokenEl.value,
                                    'Content-Type': 'application/json'
                                },
                                keepalive: true
                            });
                        }
                    }
                } else if (!isFocused && wasFocused) {
                    wasFocused = false;
                }
                requestAnimationFrame(check);
            }
            requestAnimationFrame(check);
        })();
    }

    function decodeHtml(str) {
        var txt = document.createElement('textarea');
        txt.innerHTML = str;
        return txt.value;
    }

    // Cards de anúncio na home — insere cards baseado nas colunas do grid
    var adCardsInitialized = false;
    
    function initAdCards() {
        var adCards = Array.from(document.querySelectorAll('.ad-card-wrapper'));
        if (adCards.length === 0) return;

        // Renderiza cada card em iframe isolado para evitar colisão de atOptions global
        adCards.forEach(function(card) {
            if (card.dataset.rendered) return;
            var isScript = card.getAttribute('data-is-script') === '1';
            if (!isScript) {
                var html = decodeHtml(card.getAttribute('data-ad-html') || '');
                var cont = card.querySelector('.ad-script-container');
                if (cont && html) {
                    cont.innerHTML = '<a href=\"' + html + '\" target=\"_blank\" rel=\"noopener sponsored\" class=\"ad-link\"><span class=\"ad-badge\">Access</span></a>';
                }
                card.dataset.rendered = '1';
                return;
            }
            var raw = card.getAttribute('data-ad-html') || '';
            var decoded = decodeHtml(raw);
            var container = card.querySelector('.ad-script-container');
            if (container && decoded) {
                createAdIframe(decoded, container, card.getAttribute('data-ad-id'));
            }
            card.dataset.rendered = '1';
        });

        // Não mostrar cards de anúncio ao filtrar por categoria ou busca
        var params = new URLSearchParams(window.location.search);
        if (params.has('category') || params.has('q')) {
            return;
        }

        // Se já inicializou, não faz nada (mantém posições fixas)
        if (adCardsInitialized) return;

        var grid = adCards[0].parentElement;
        
        // Pega apenas cards de publicação (não anúncios)
        var pubCards = Array.from(grid.children).filter(function(el) {
            return !el.classList.contains('ad-card-wrapper');
        });

        if (pubCards.length < 2) {
            adCards.forEach(function(card) { 
                card.style.display = '';
            });
            return;
        }

        // Calcula número de colunas baseado na largura do grid
        // CSS usa minmax(220px, 1fr) com gap 24px
        // Fórmula: N colunas = N * 244 - 24
        var gridWidth = grid.offsetWidth;
        var columns;
        if (gridWidth >= 1196) {
            columns = 5;
        } else if (gridWidth >= 952) {
            columns = 4;
        } else if (gridWidth >= 708) {
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

        // Posiciona os cards que serão mostrados
        for (var i = 0; i < adsToShow; i++) {
            var adCard = adCards[i];
            var randomPos = Math.floor(Math.random() * (maxPos - minPos + 1)) + minPos;

            // Recalcula pubCards pois a ordem pode ter mudado
            pubCards = Array.from(grid.children).filter(function(el) {
                return !el.classList.contains('ad-card-wrapper');
            });

            if (randomPos >= pubCards.length) {
                grid.appendChild(adCard);
            } else {
                grid.insertBefore(adCard, pubCards[randomPos]);
            }
            adCard.style.display = '';
        }
        
        // Esconde os cards que não serão mostrados
        for (var i = adsToShow; i < adCards.length; i++) {
            adCards[i].style.display = 'none';
        }
        
        adCardsInitialized = true;
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
    function initAll() {
        initCarousel();
        initAdCards();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }
})();
