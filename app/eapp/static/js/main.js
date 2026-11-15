function onDateInput(date) {
    let year = date.split('-')[0]
    let today_year = new Date().getFullYear()

    if (year - today_year >= -1 && year - today_year <= 1) {
        console.log(date)
        window.location.assign("/danhsachkham?q=".concat(date))
    }
}