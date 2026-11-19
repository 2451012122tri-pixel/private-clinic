function drawChart(data, labels, title, ctxId = 'myChart', type = 'pie') {
    const ctx = document.getElementById(ctxId);
    if (!ctx || typeof Chart === 'undefined') return;

    const existingChart = Chart.getChart(ctx);
    if (existingChart) {
        existingChart.destroy();
    }

    const colors = [];
    for (let i = 0; i < data.length; i++) {
        colors.push(`rgba(${parseInt(Math.random() * 220)}, ${parseInt(Math.random() * 220)}, ${parseInt(Math.random() * 220)}, 0.7)`);
    }

    const options = {
        responsive: true
    };
    if (type === 'bar') {
        options.scales = {
            y: {
                beginAtZero: true
            }
        };
    }

    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderWidth: 1,
                backgroundColor: colors
            }]
        },
        options: options
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput || !window.location.pathname.includes('/admin/thuoc')) return;

    fetch('/admin/thuoc/api/ten-thuoc')
        .then(res => res.json())
        .then(dsThuoc => {
            const datalist = document.createElement('datalist');
            datalist.id = 'thuoc-db-list';

            const select = document.createElement('select');
            select.className = 'form-control mr-2';
            select.style.maxWidth = '240px';

            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = dsThuoc.length > 0
                ? `-- Chọn thuốc (${dsThuoc.length}) --`
                : '-- Chưa có thuốc trong CSDL --';
            select.appendChild(defaultOpt);

            if (dsThuoc.length === 0) {
                select.disabled = true;
            } else {
                dsThuoc.forEach(ten => {
                    const dlOpt = document.createElement('option');
                    dlOpt.value = ten;
                    datalist.appendChild(dlOpt);

                    const opt = document.createElement('option');
                    opt.value = ten;
                    opt.textContent = ten;
                    if (searchInput.value === ten) {
                        opt.selected = true;
                    }
                    select.appendChild(opt);
                });
            }

            document.body.appendChild(datalist);
            searchInput.setAttribute('list', 'thuoc-db-list');
            searchInput.setAttribute('autocomplete', 'off');

            select.addEventListener('change', function () {
                searchInput.value = this.value;
                searchInput.form.submit();
            });

            searchInput.parentNode.insertBefore(select, searchInput);
        });
});