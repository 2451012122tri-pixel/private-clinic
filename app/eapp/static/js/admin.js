function drawAdminIndexChart() {
    const payload = document.getElementById('index-chart-payload');
    const ctx = document.getElementById('myChart');
    if (!payload || !ctx || typeof Chart === 'undefined') return;

    const labels = JSON.parse(payload.dataset.labels || '[]');
    const data = JSON.parse(payload.dataset.values || '[]');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu (VNĐ)',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function drawAdminStatsCharts() {
    const payload = document.getElementById('stats-payload');
    if (!payload || typeof Chart === 'undefined') return;

    const dtLabels = JSON.parse(payload.dataset.dtLabels || '[]');
    const dtData = JSON.parse(payload.dataset.dtValues || '[]');
    const thuocLabels = JSON.parse(payload.dataset.thuocLabels || '[]');
    const thuocData = JSON.parse(payload.dataset.thuocValues || '[]');

    const ctxDt = document.getElementById('chartDoanhThu');
    if (ctxDt) {
        new Chart(ctxDt, {
            type: 'bar',
            data: {
                labels: dtLabels,
                datasets: [{
                    label: 'Doanh thu (VNĐ)',
                    data: dtData,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    const ctxThuoc = document.getElementById('chartThuoc');
    if (ctxThuoc) {
        new Chart(ctxThuoc, {
            type: 'pie',
            data: {
                labels: thuocLabels,
                datasets: [{
                    label: 'Số lượng đã dùng',
                    data: thuocData,
                    borderWidth: 1
                }]
            }
        });
    }
}

window.onload = function () {
    drawAdminIndexChart();
    drawAdminStatsCharts();
};