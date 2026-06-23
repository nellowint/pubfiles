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
            document.querySelectorAll('.js-lang-dropdown.open').forEach(d => {
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
        document.querySelectorAll('.js-lang-dropdown.open').forEach(d => {
            d.classList.remove('open');
        });
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

    if (activeId) {
        document.querySelectorAll(`.id-filha-${activeId}`).forEach(btn => {
            btn.classList.add('active');
        });

        const activeParentBtns = document.querySelectorAll(`.id-pai-${activeId}`);
        const targetSubBlocks = document.querySelectorAll(`.sub-bloco-pai-${activeId}`);

        if (activeParentBtns.length > 0 && targetSubBlocks.length > 0) {
            activeParentBtns.forEach(btn => btn.classList.add('active'));
            targetSubBlocks.forEach(block => { block.style.display = 'block'; });
        } else {
            const activeChildBtns = document.querySelectorAll(`.id-filha-${activeId}`);
            activeChildBtns.forEach(btn => {
                const parentContainer = btn.closest('.nav-children-row, .drawer-subcategories');
                if (parentContainer) {
                    parentContainer.style.display = 'block';

                    const classMatch = parentContainer.className.match(/sub-bloco-pai-(\d+)/);
                    if (classMatch && classMatch[1]) {
                        document.querySelectorAll(`.id-pai-${classMatch[1]}`).forEach(rootBtn => {
                            rootBtn.classList.add('active');
                        });
                    }
                }
            });
        }
    }
})();
