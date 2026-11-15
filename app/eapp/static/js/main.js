function onDateInput(date) {
    let year = date.split('-')[0]
    let today_year = new Date().getFullYear()

    if (year - today_year >= -1 && year - today_year <= 1) {
        console.log(date)
        window.location.assign("/danhsachkham?q=".concat(date))
    }
}

function deleteBenhNhan(ttk_id) {
    if (confirm("Bạn có chắc chắn muốn xóa bệnh nhân này ra khỏi danh sách này không?") == true) {
        fetch(`/danhsachkham/delete/${ttk_id}`, { method: 'DELETE'})
            .then(data => {
                location.reload()
            })
    }
}

function deleteThongTinKhamSession() {
    if (confirm("Lưu thay đổi?") == true) {
        fetch(`/danhsachkham`, { method: 'PATCH'})
            .then(data => {
                location.reload()
            })
    }
}