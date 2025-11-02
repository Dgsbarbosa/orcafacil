document.addEventListener('DOMContentLoaded', () => {
    const menuItems = document.querySelectorAll('.menu-item');

    function loadSection(section) {
        window.loadContent(section, () => {
            if (section === 'clients' && window.initClients) window.initClients();
            if (section === 'budgets' && window.initBudgets) window.initBudgets();
            // adicione outros inits conforme criar
        });
    }

    // Carrega seção inicial
    loadSection('profile');

    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            loadSection(item.dataset.section);
        });
    });
});
