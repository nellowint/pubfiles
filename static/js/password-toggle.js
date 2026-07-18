(function () {
    function init() {
        document.querySelectorAll('input[type="password"]').forEach(function (input) {
            if (input.dataset.passwordToggle) return;
            input.dataset.passwordToggle = '1';

            var wrapper = document.createElement('div');
            wrapper.className = 'password-field';
            wrapper.style.cssText = 'position:relative;width:100%;';

            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);

            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'password-toggle-btn';
            btn.style.cssText =
                'position:absolute;right:10px;top:50%;transform:translateY(-50%);' +
                'background:transparent;border:none;outline:none;box-shadow:none;' +
                'margin:0;padding:4px;cursor:pointer;line-height:0;' +
                'display:flex;align-items:center;justify-content:center;';
            var currentPadding = parseFloat(getComputedStyle(input).paddingRight) || 0;
            if (currentPadding < 40) {
                input.style.paddingRight = '42px';
            }

            btn.setAttribute('aria-label', 'Mostrar senha');
            btn.innerHTML =
                '<svg class="icon-eye" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
                    '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"></path>' +
                    '<circle cx="12" cy="12" r="3"></circle>' +
                '</svg>' +
                '<svg class="icon-eye-off" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none;">' +
                    '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-10-8-10-8a18.45 18.45 0 0 1 5.06-5.94"></path>' +
                    '<path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 10 8 10 8a18.5 18.5 0 0 1-2.16 3.19"></path>' +
                    '<path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"></path>' +
                    '<line x1="1" y1="1" x2="23" y2="23"></line>' +
                '</svg>';
            wrapper.appendChild(btn);

            btn.addEventListener('click', function () {
                var isPwd = input.type === 'password';
                input.type = isPwd ? 'text' : 'password';
                btn.querySelector('.icon-eye').style.display = isPwd ? 'none' : '';
                btn.querySelector('.icon-eye-off').style.display = isPwd ? '' : 'none';
                btn.setAttribute('aria-label', isPwd ? 'Ocultar senha' : 'Mostrar senha');
                input.focus();
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();