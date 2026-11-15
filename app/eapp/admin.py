import hashlib
from datetime import datetime
from flask import redirect
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from wtforms.fields.numeric import FloatField, IntegerField

from eapp import app, db, dao
from eapp.models import User, UserRoleEnum, QuyDinh, DonViThuoc, Thuoc


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        now = datetime.now()
        thang = now.month
        nam = now.year
        # Nếu dao.py chưa có hàm stats_doanh_thu_thang, tạm để doanh_thu, tong_dt = [], 0 rồi cập nhật ở nhánh stats
        doanh_thu, tong_dt = dao.stats_doanh_thu_thang(thang, nam) if hasattr(dao, 'stats_doanh_thu_thang') else ([], 0)
        return self.render('admin/index.html',
                           tong_thuoc=dao.count_thuoc(),
                           tong_doanh_thu=tong_dt,
                           doanh_thu_stats=doanh_thu,
                           thang=thang,
                           nam=nam,
                           quy_dinh=dao.get_quy_dinh())


admin = Admin(app=app, name='Quản Trị Phòng Mạch Tư', index_view=MyAdminIndex())


class AdminAuthenticated(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.QUAN_TRI


class UserView(AdminAuthenticated):
    column_list = ['id', 'name', 'username', 'user_role']
    column_labels = {
        'name': 'Họ tên nhân viên',
        'username': 'Tên đăng nhập',
        'password': 'Mật khẩu',
        'user_role': 'Vai trò'
    }
    column_searchable_list = ['name', 'username']
    column_filters = ['user_role']
    edit_modal = True

    def on_model_change(self, form, model, is_created):
        if is_created or form.password.object_data != model.password:
            model.password = hashlib.md5(model.password.strip().encode('utf-8')).hexdigest()

    def on_model_delete(self, model):
        if model.id == current_user.id:
            raise ValueError("Không thể tự xóa tài khoản quản trị đang đăng nhập!")


class QuyDinhView(AdminAuthenticated):
    can_create = False
    can_delete = False
    edit_modal = True
    column_list = ['so_benh_nhan_toi_da', 'tien_kham']
    column_labels = {
        'so_benh_nhan_toi_da': 'Số bệnh nhân khám tối đa / ngày',
        'tien_kham': 'Tiền khám mặc định (VNĐ)'
    }
    form_overrides = {
        'so_benh_nhan_toi_da': IntegerField,
        'tien_kham': FloatField
    }

    def on_model_change(self, form, model, is_created):
        if model.so_benh_nhan_toi_da is None or model.so_benh_nhan_toi_da <= 0:
            raise ValueError("Số bệnh nhân tối đa trong ngày phải lớn hơn 0!")
        if model.tien_kham is None or model.tien_kham < 0:
            raise ValueError("Tiền khám không được nhỏ hơn 0!")


class DonViThuocView(AdminAuthenticated):
    column_list = ['id', 'ten_don_vi']
    column_labels = {
        'ten_don_vi': 'Tên đơn vị tính',
        'thuocs': 'Danh sách thuốc đang dùng đơn vị này'
    }
    column_searchable_list = ['ten_don_vi']
    edit_modal = True
    can_view_details = True
    details_modal = True
    column_details_list = ['id', 'ten_don_vi', 'thuocs']

    def on_model_change(self, form, model, is_created):
        if not model.ten_don_vi or not model.ten_don_vi.strip():
            raise ValueError("Tên đơn vị thuốc không được để trống!")
        model.ten_don_vi = model.ten_don_vi.strip()

    def on_model_delete(self, model):
        if dao.is_don_vi_used(model.id):
            raise ValueError(f"Không thể xóa đơn vị '{model.ten_don_vi}' vì đang có thuốc sử dụng đơn vị này!")


class ThuocView(AdminAuthenticated):
    column_list = ['id', 'ten_thuoc', 'don_vi_thuoc', 'don_gia']
    column_labels = {
        'ten_thuoc': 'Tên thuốc',
        'don_vi_thuoc': 'Đơn vị tính',
        'don_gia': 'Đơn giá (VNĐ)',
        'hinh_anh': 'Hình ảnh thuốc (URL)'
    }
    can_export = True
    column_searchable_list = ['ten_thuoc']
    column_filters = ['id', 'ten_thuoc', 'don_gia', 'don_vi_thuoc.ten_don_vi']
    edit_modal = True
    can_view_details = True
    details_modal = True
    form_overrides = {
        'don_gia': FloatField
    }

    def on_model_change(self, form, model, is_created):
        if not model.ten_thuoc or not model.ten_thuoc.strip():
            raise ValueError("Tên thuốc không được để trống!")
        if model.don_gia is None or model.don_gia < 0:
            raise ValueError("Đơn giá thuốc phải lớn hơn hoặc bằng 0!")
        model.ten_thuoc = model.ten_thuoc.strip()

    def on_model_delete(self, model):
        if dao.is_thuoc_used(model.id):
            raise ValueError(f"Không thể xóa thuốc '{model.ten_thuoc}' vì đã được kê trong phiếu khám!")


class BaseAdminAuthenticated(BaseView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRoleEnum.QUAN_TRI


class LogoutView(BaseAdminAuthenticated):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


admin.add_view(QuyDinhView(QuyDinh, db.session, name='Quy định'))
admin.add_view(DonViThuocView(DonViThuoc, db.session, name='Đơn vị thuốc'))
admin.add_view(ThuocView(Thuoc, db.session, name='Quản lý thuốc'))
admin.add_view(UserView(User, db.session, name='Tài khoản nhân viên'))
admin.add_view(LogoutView(name='Đăng xuất'))