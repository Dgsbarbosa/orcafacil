function initClients() {
    const tableDiv = document.getElementById('clients-table');
    const searchInput = document.getElementById('input-search-clients');
    const statusSelect = document.getElementById('filter-status');
    const btnNewClient = document.getElementById('new-client');

    if (!tableDiv) return;

    // função isolada apenas para carregar os dados
    function loadClients() {
        const search = searchInput?.value || '';
        const status = statusSelect?.value || '';

        fetch(`/core/clients/?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            tableDiv.innerHTML = data.html;
            // ❌ NÃO chamar initClients() novamente aqui!
            // ✅ Apenas reanexar eventos da tabela (se houver botões dentro dela)
            attachTableEvents();
        })
        .catch(err => console.error("Erro ao carregar clientes:", err));
    }

    // reanexa eventos internos da tabela (botões editar, excluir, etc)
    function attachTableEvents() {
        document.querySelectorAll('.btn-edit-client').forEach(btn => {
            btn.addEventListener('click', () => {
                console.log("Editar cliente:", btn.dataset.id);
            });
        });
    }

    // Carrega a primeira vez
    loadClients();

    // Define eventos dos filtros e do botão de novo cliente
    if (searchInput) searchInput.addEventListener('input', loadClients);
    if (statusSelect) statusSelect.addEventListener('change', loadClients);
    if (btnNewClient) btnNewClient.addEventListener('click', () => {
        console.log("Abrindo formulário de novo cliente...");
        window.loadContent('client_form');
    });
}

window.initClients = initClients;
