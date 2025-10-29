// Função global para carregar seções via AJAX
window.loadContent = function (section, callback = null) {
    fetch(`dashboard/${section}/`)
        .then(res => res.json())
        .then(data => {
            const contentArea = document.getElementById('content-area');
            contentArea.innerHTML = data.html;
            if (callback) callback(); // reexecuta init da seção
        })
        .catch(err => console.error("Erro ao carregar conteúdo:", err));
};
