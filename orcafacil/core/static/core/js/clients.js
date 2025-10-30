// ---------------------------
// Função para pegar CSRF token
// ---------------------------
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ---------------------------
// Delegação global para excluir cliente
// ---------------------------
document.addEventListener('click', function (e) {
    const deleteBtn = e.target.closest('.delete-client');
    if (!deleteBtn) return;

    const clientId = deleteBtn.dataset.client_id;
    if (!clientId) return;

    if (!confirm("Tem certeza que deseja excluir este cliente?")) return;

    fetch(`client/delete/${clientId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(res => res.json())
        .then(data => {
            
            if (data.success) {
                // Atualiza tabela
                
                 window.loadContent('clients', () => {
        window.loadClients(); // só chama depois que a seção estiver carregada
    });
                
                
            } else {
                alert("Erro ao excluir: " + (data.error || "Erro desconhecido"));
            }
        })
        .catch(err => console.error(err));
});

// ---------------------------
// Delegação global para editar/visualizar cliente
// ---------------------------
document.addEventListener('click', function (e) {
    const editBtn = e.target.closest('.edit-client');
    const viewBtn = e.target.closest('.view-client');

    if (editBtn) {
        const id = editBtn.dataset.id;
        window.loadContent(`client/edit/${id}`);
    }

    if (viewBtn) {
        const id = viewBtn.dataset.id;
        window.loadContent(`client/view/${id}`);
    }
});

// ---------------------------
// Carrega tabela de clientes
// ---------------------------
window.loadClients = function () {
    const tableDiv = document.getElementById('clients-table');
    const searchInput = document.getElementById('input-search-clients');
    const statusSelect = document.getElementById('filter-status');

    if (!tableDiv) return;

    const search = searchInput?.value || '';
    const status = statusSelect?.value || '';

    fetch(`/core/clients/?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            tableDiv.innerHTML = data.html; // tabela atualizada
        })
        .catch(err => console.error(err));
}

// ---------------------------
// Inicializa filtros, busca e botão novo cliente
// ---------------------------
window.initClients = function () {
    const searchInput = document.getElementById('input-search-clients');
    const statusSelect = document.getElementById('filter-status');
    const btnNewClient = document.getElementById('new-client');

    if (searchInput) searchInput.addEventListener('input', window.loadClients);
    if (statusSelect) statusSelect.addEventListener('change', window.loadClients);

    if (btnNewClient) {
        btnNewClient.addEventListener('click', () => {
            window.loadContent('client_form');
        });
    }

    // Carrega tabela inicial
    window.loadClients();
}
