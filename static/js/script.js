
    document.addEventListener("DOMContentLoaded", function () {
        setTimeout(function () {
            let alerts = document.querySelectorAll('.alert');
            alerts.forEach(function (alert) {
                alert.classList.remove('show');
                alert.addEventListener('transitionend', function () {
                    alert.remove();
                });
            });
        }, 5000);
    });
document.getElementById('submit-btn').addEventListener('click', function(event) {
    const truffledFlavor = document.getElementById('truffled-flavor-select').value;
    const traditionalFlavor = document.getElementById('traditional-flavor-select').value;

    // Se ambos os sabores não forem selecionados, impede o envio
    if (!truffledFlavor && !traditionalFlavor) {
        event.preventDefault(); // Impede o envio do formulário
        alert('{% trans "Please select at least one flavor: truffled or traditional." %}');
    }
});

