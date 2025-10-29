function initClients() {
    const tableDiv = document.getElementById('clients-table');
    const searchInput = document.getElementById('input-search-clients');
    const statusSelect = document.getElementById('filter-status');
    const btnNewClient = document.getElementById('new-client');

    if (!tableDiv) return;

    function loadClients() {
        const search = searchInput?.value || '';
        const status = statusSelect?.value || '';

        fetch(`/core/clients/?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            tableDiv.innerHTML = data.html;
            // ❌ REMOVIDO: initClients();
            // Se o conteúdo dentro da tabela tiver botões com eventos, 
            // você pode chamá-los aqui manualmente, ex:
            // attachRowEvents();
        })
        .catch(err => console.error("Erro ao carregar clientes:", err));
    }

    loadClients();

    if (searchInput) searchInput.addEventListener('input', loadClients);
    if (statusSelect) statusSelect.addEventListener('change', loadClients);

    if (btnNewClient) {
        btnNewClient.addEventListener('click', () => {
            console.log("Abrindo formulário de novo cliente...");
            window.loadContent('client_form');
        });
    }
}

window.initClients = initClients;
