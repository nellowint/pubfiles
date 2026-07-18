(function () {
    function init() {
        document.querySelectorAll('.search-input, input[name="q"]').forEach(function (input) {
            if (input.dataset.searchClear) return;
            input.dataset.searchClear = '1';

            var form = input.closest('form');
            var parent = input.parentNode;

            var wrapper = document.createElement('div');
            wrapper.className = 'search-field';
            wrapper.style.cssText = 'position:relative;width:100%;';
            parent.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'search-clear-btn';
            btn.setAttribute('aria-label', 'Limpar pesquisa');
            btn.style.cssText =
                'position:absolute;right:8px;top:50%;transform:translateY(-50%);' +
                'background:transparent;border:none;outline:none;box-shadow:none;' +
                'margin:0;padding:4px;cursor:pointer;line-height:0;' +
                'display:none;align-items:center;justify-content:center;' +
                'color:var(--text-color);opacity:0.6;transition:opacity 150ms ease;';
            btn.innerHTML =
                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                    '<line x1="18" y1="6" x2="6" y2="18"></line>' +
                    '<line x1="6" y1="6" x2="18" y2="18"></line>' +
                '</svg>';
            wrapper.appendChild(btn);

            btn.addEventListener('mouseenter', function () { btn.style.opacity = '1'; });
            btn.addEventListener('mouseleave', function () { btn.style.opacity = '0.6'; });

            function toggleBtn() {
                btn.style.display = input.value ? 'flex' : 'none';
                var currentPadding = parseFloat(getComputedStyle(input).paddingRight) || 0;
                if (input.value && currentPadding < 34) {
                    input.style.paddingRight = '34px';
                } else if (!input.value) {
                    input.style.paddingRight = '';
                }
            }

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                input.value = '';
                toggleBtn();
                if (form && form.tagName === 'FORM') {
                    form.submit();
                } else {
                    input.focus();
                }
            });

            input.addEventListener('input', toggleBtn);
            toggleBtn();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();