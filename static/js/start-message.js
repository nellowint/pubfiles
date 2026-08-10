(function() {
    const modal = document.getElementById('startModal');
    if (!modal) return;

    const STORAGE_KEY = 'start_message_dismissed';
    const dontShow = document.getElementById('startModalDontShow');
    const confirmBtn = document.getElementById('startModalConfirm');
    const exitBtn = document.getElementById('startModalExit');

    const isDismissed = () => localStorage.getItem(STORAGE_KEY) === '1';
    if (isDismissed()) return;

    const remember = () => {
        if (dontShow && dontShow.checked) {
            localStorage.setItem(STORAGE_KEY, '1');
        }
    };

    const close = () => {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    };

    const open = () => {
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    };

    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            remember();
            close();
        });
    }

    if (exitBtn) {
        exitBtn.addEventListener('click', () => {
            remember();
            close();
            try {
                const blankTab = window.open('about:blank', '_blank');
                if (blankTab) blankTab.focus();
            } catch (e) { /* popup bloqueado */ }
            setTimeout(() => {
                window.location.href = 'about:blank';
                setTimeout(() => window.close(), 50);
            }, 50);
        });
    }

    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            remember();
            close();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            remember();
            close();
        }
    });

    open();
})();
