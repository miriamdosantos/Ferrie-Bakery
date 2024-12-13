
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
