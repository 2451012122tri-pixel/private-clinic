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