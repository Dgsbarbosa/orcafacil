function initClients() {
    const tableDiv = document.getElementById('clients-table');
    const searchInput = document.getElementById('input-search-clients');
    const statusSelect = document.getElementById('filter-status');
    const btnNewClient = document.getElementById('new-client');

    if (!tableDiv) return;

    // ---- Função que recarrega os clientes ----
    function loadClients() {
        const search = searchInput?.value || '';
        const status = statusSelect?.value || '';

        fetch(`/core/clients/?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            tableDiv.innerHTML = data.html;
        })
        .catch(err => console.error("Erro ao carregar clientes:", err));
    }

    // ---- Eventos de filtro e busca ----
    if (searchInput) searchInput.addEventListener('input', loadClients);
    if (statusSelect) statusSelect.addEventListener('change', loadClients);

    // ---- Novo cliente ----
    if (btnNewClient) {
        btnNewClient.addEventListener('click', () => {
            window.loadContent('client_form');
        });
    }

    // ---- DELEGAÇÃO: clique nos ícones ----
    tableDiv.addEventListener('click', (e) => {
        const editIcon = e.target.closest('.edit-client');
        const viewIcon = e.target.closest('.view-client');

        if (editIcon) {
            const id = editIcon.dataset.id;
            console.log("Editar cliente:", id);
            // Carrega seção de edição
            window.loadContent(`client/edit/${id}`);
        }

        if (viewIcon) {
            const id = viewIcon.dataset.id;
            console.log("Visualizar cliente:", id);
            // Carrega seção de visualização
            window.loadContent(`client/view/${id}`);
        }
    });

    // ---- Carrega lista inicial ----
    loadClients();
}

window.initClients = initClients;
