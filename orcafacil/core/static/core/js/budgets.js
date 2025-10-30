// ---------------------------
// Pega o CSRF token
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
// Delegação global para excluir orçamento
// ---------------------------
document.addEventListener('click', function (e) {
    const deleteBtn = e.target.closest('.delete-budget');
    if (!deleteBtn) return;

    const budgetId = deleteBtn.dataset.budget_id;
    if (!budgetId) return;

    if (!confirm("Tem certeza que deseja excluir este orçamento?")) return;

    fetch(`budget/delete/${budgetId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.loadContent('budgets', () => {
                    window.loadBudgets();
                });
            } else {
                alert("Erro ao excluir: " + (data.error || "Erro desconhecido"));
            }
        })
        .catch(err => console.error(err));
});

// ---------------------------
// Delegação global para editar/visualizar orçamento
// ---------------------------
document.addEventListener('click', function (e) {
    const editBtn = e.target.closest('.edit-budget');
    const viewBtn = e.target.closest('.view-budget');

    if (editBtn) {
        const id = editBtn.dataset.id;
        window.loadContent(`budget/edit/${id}`);
    }

    if (viewBtn) {
        const id = viewBtn.dataset.id;
        window.loadContent(`budget/view/${id}`);
    }
});

// ---------------------------
// Carrega tabela de orçamentos
// ---------------------------
window.loadBudgets = function () {
    const tableDiv = document.getElementById('budgets-table');
    const searchInput = document.getElementById('input-search-budgets');
    const statusSelect = document.getElementById('filter-status-budgets');

    if (!tableDiv) return;

    const search = searchInput?.value || '';
    const status = statusSelect?.value || '';

    fetch(`/core/budgets/?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            tableDiv.innerHTML = data.html;
        })
        .catch(err => console.error(err));
}

// ---------------------------
// Inicializa filtros, busca e botão novo orçamento
// ---------------------------
window.initBudgets = function () {
    const searchInput = document.getElementById('input-search-budgets');
    const statusSelect = document.getElementById('filter-status-budgets');
    const btnNewBudget = document.getElementById('new-budget');

    if (searchInput) searchInput.addEventListener('input', window.loadBudgets);
    if (statusSelect) statusSelect.addEventListener('change', window.loadBudgets);

    if (btnNewBudget) {
        btnNewBudget.addEventListener('click', () => {
            window.loadContent('budget_form');
        });
    }

    window.loadBudgets();
};
