document.querySelectorAll('.js-theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        let newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
});

(function() {
    const languageForm = document.getElementById('languageForm');
    const languageInput = document.getElementById('languageInput');

    document.querySelectorAll('.lang-selector').forEach(selector => {
        const toggle = selector.querySelector('.js-lang-toggle');
        const dropdown = selector.querySelector('.js-lang-dropdown');
        if (!toggle || !dropdown) return;

        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.js-lang-dropdown.open, .js-user-menu-dropdown.open').forEach(d => {
                if (d !== dropdown) d.classList.remove('open');
            });
            dropdown.classList.toggle('open');
        });

        dropdown.querySelectorAll('.js-lang-option').forEach(option => {
            option.addEventListener('click', () => {
                if (languageForm && languageInput) {
                    languageInput.value = option.dataset.lang;
                    languageForm.submit();
                }
            });
        });
    });

    document.addEventListener('click', () => {
        document.querySelectorAll('.js-lang-dropdown.open, .js-user-menu-dropdown.open').forEach(d => {
            d.classList.remove('open');
        });
    });
})();

(function() {
    document.querySelectorAll('.user-menu-selector').forEach(selector => {
        const toggle = selector.querySelector('.js-user-menu-toggle');
        const dropdown = selector.querySelector('.js-user-menu-dropdown');
        if (!toggle || !dropdown) return;

        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            document.querySelectorAll('.js-lang-dropdown.open, .js-user-menu-dropdown.open').forEach(d => {
                if (d !== dropdown) d.classList.remove('open');
            });
            const isOpen = dropdown.classList.toggle('open');
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        dropdown.addEventListener('click', (e) => e.stopPropagation());
    });
})();

(function() {
    const drawerToggle = document.getElementById('navMobileToggle');
    const drawerNav = document.getElementById('drawerNav');
    const drawerOverlay = document.getElementById('drawerOverlay');
    const drawerClose = document.getElementById('drawerClose');

    if (!drawerToggle || !drawerNav || !drawerOverlay) return;

    function openDrawer() {
        drawerNav.classList.add('open');
        drawerOverlay.classList.add('open');
        document.body.style.overflow = 'hidden';
        drawerToggle.setAttribute('aria-expanded', 'true');
        drawerNav.setAttribute('aria-hidden', 'false');
    }

    function closeDrawer() {
        drawerNav.classList.remove('open');
        drawerOverlay.classList.remove('open');
        document.body.style.overflow = '';
        drawerToggle.setAttribute('aria-expanded', 'false');
        drawerNav.setAttribute('aria-hidden', 'true');
    }

    drawerToggle.addEventListener('click', () => {
        if (drawerNav.classList.contains('open')) {
            closeDrawer();
        } else {
            openDrawer();
        }
    });

    if (drawerClose) drawerClose.addEventListener('click', closeDrawer);
    drawerOverlay.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawerNav.classList.contains('open')) {
            closeDrawer();
        }
    });
})();

(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const activeId = urlParams.get('category');
    if (!activeId) return;

    document.querySelectorAll('.cat-' + activeId).forEach(btn => btn.classList.add('active'));

    let cur = activeId;
    while (cur) {
        document.querySelectorAll('.children-of-' + cur).forEach(block => {
            block.classList.add('open');
        });
        const btn = document.querySelector('.cat-' + cur);
        cur = btn ? (btn.dataset.parentId || '') : '';
    }
})();
