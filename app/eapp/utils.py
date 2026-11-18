from eapp import dao

def gioi_tinh_str_to_enum(str_gioi_tinh):
    enum_gioi_tinh = dao.get_Gioi_Tinh()

    if (str_gioi_tinh == "Nam"):
        return enum_gioi_tinh.NAM
    if (str_gioi_tinh == "Nữ"):
        return enum_gioi_tinh.NU

    return None