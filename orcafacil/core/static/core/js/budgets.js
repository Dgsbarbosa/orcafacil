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
        const totalFormsInput = document.querySelector("#id_services-TOTAL_FORMS");
        let formCount = parseInt(totalFormsInput.value, 10);

        const formContainer = document.getElementById("services-forms");
        const firstForm = formContainer.querySelector(".card-new-service");

        if (!firstForm) {
            console.error("Form base não encontrado!");
            return;
        }

        // Clona o primeiro formulário
        const newForm = firstForm.cloneNode(true);

        // Limpa valores e renomeia corretamente todos os índices
        newForm.querySelectorAll("input, textarea, select, label").forEach(el => {
            if (el.name)
                el.name = el.name.replaceAll(/services-\d+-/g, `services-${formCount}-`);
            if (el.id)
                el.id = el.id.replaceAll(/services-\d+-/g, `services-${formCount}-`);
            if (el.htmlFor)
                el.htmlFor = el.htmlFor.replaceAll(/services-\d+-/g, `services-${formCount}-`);

            // Limpa campos visíveis
            if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
                if (el.type === "checkbox" || el.type === "radio") el.checked = false;
                else if (el.type !== "hidden") el.value = "";
            }
        });

        // Adiciona o novo formulário
        formContainer.appendChild(newForm);

        // Atualiza o contador de formulários
        totalFormsInput.value = formCount + 1;
    });
};
