// ======================================================
//  budgets.js — controle de CRUD e formulários dinâmicos
// ======================================================

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

// ======================================================
// EXCLUSÃO DE ORÇAMENTO (delegação global)
// ======================================================
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
                // Recarrega lista de orçamentos
                window.loadContent('budgets', () => {
                    window.loadBudgets();
                });
            } else {
                alert("Erro ao excluir: " + (data.error || "Erro desconhecido"));
            }
        })
        .catch(err => console.error(err));
});

// ======================================================
// EDIÇÃO / VISUALIZAÇÃO DE ORÇAMENTO
// ======================================================
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

// ======================================================
// CARREGAR LISTA DE ORÇAMENTOS
// ======================================================
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
};

// ======================================================
// INICIALIZAÇÃO DA TELA DE ORÇAMENTOS
// ======================================================
window.initBudgets = function () {
    const searchInput = document.getElementById('input-search-budgets');
    const statusSelect = document.getElementById('filter-status-budgets');
    const btnNewBudget = document.getElementById('new-budget');

    if (searchInput) searchInput.addEventListener('input', window.loadBudgets);
    if (statusSelect) statusSelect.addEventListener('change', window.loadBudgets);

    if (btnNewBudget) {
        btnNewBudget.addEventListener('click', () => {
            // Carrega o formulário de novo orçamento
            window.loadContent('budget_form', () => {
                // Inicializa JS do formulário
                window.initNewBudgetForm();
            });
        });
    }

    // Carrega tabela inicial
    window.loadBudgets();
};

// ======================================================
// FORM DINÂMICO DE NOVO ORÇAMENTO (SERVIÇOS)
// ======================================================
window.initNewBudgetForm = function () {
    const addServiceBtn = document.getElementById('add-service');
    if (!addServiceBtn) return;

    addServiceBtn.addEventListener("click", () => {
        const totalForms = document.querySelector("#id_service_set-TOTAL_FORMS");
        const formCount = parseInt(totalForms.value);
        const newForm = document.querySelectorAll('.card-new-service')[0].cloneNode(true);

        // Limpa os valores dos inputs no clone
        newForm.querySelectorAll('input, textarea, select').forEach(el => el.value = '');

        newForm.innerHTML = newForm.innerHTML.replaceAll(`-0-`, `-${formCount}-`);
        document.getElementById('services-forms').appendChild(newForm);
        totalForms.value = formCount + 1;
    });
};
