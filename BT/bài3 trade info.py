import hashlib
import os
import shutil
from pathlib import Path


def tinh_hash(duong_dan: str) -> str:
    """Tính SHA-512 của file (đọc từng chunk)"""
    sha512 = hashlib.sha512()
    with open(duong_dan, 'rb') as f:
        while chunk := f.read(8192):
            sha512.update(chunk)
    return sha512.hexdigest()


def hien_thi_hash(ten: str, gia_tri: str):
    print(f"   {ten}: {gia_tri[:32]}...{gia_tri[-8:]}")


def dem_ky_tu_hash_khac_nhau(hash_1: str, hash_2: str) -> int:
    """Đếm số ký tự khác nhau giữa 2 chuỗi hash."""
    do_dai = max(len(hash_1), len(hash_2))
    return sum(
        (hash_1[i] if i < len(hash_1) else None) !=
        (hash_2[i] if i < len(hash_2) else None)
        for i in range(do_dai)
    )


def tim_anh_mau(thu_muc_anh: str = "file ảnh") -> str:
    """Tìm một file ảnh mẫu trong thư mục để dùng cho bài 3."""
    duong_dan_thu_muc = Path(thu_muc_anh)
    if not duong_dan_thu_muc.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục ảnh mẫu: '{thu_muc_anh}'")

    dinh_dang_anh = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
    for tep in sorted(duong_dan_thu_muc.iterdir()):
        if tep.is_file() and tep.suffix.lower() in dinh_dang_anh:
            return str(tep)

    raise FileNotFoundError(f"Không tìm thấy file ảnh nào trong '{thu_muc_anh}'")


# ══════════════════════════════════════════════
#  PHÍA NGƯỜI GỬI
# ══════════════════════════════════════════════

def nguoi_gui(file_goc: str, thu_muc_gui: str):
    """
    Người gửi:
      1. Tính hash của ảnh gốc
      2. Đóng gói ảnh + hash vào thư mục gửi (giả lập truyền mạng)
    """
    print("\n" + "═" * 60)
    print("📤  NGƯỜI GỬI")
    print("═" * 60)

    # Bước 1: Tính hash
    hash_goc = tinh_hash(file_goc)
    print(f"\n  [1] Tính SHA-512 của ảnh gốc '{file_goc}':")
    hien_thi_hash("Hash", hash_goc)
    print(f"      Kích thước ảnh gốc: {os.path.getsize(file_goc):,} bytes")

    # Bước 2: Tạo thư mục gửi
    os.makedirs(thu_muc_gui, exist_ok=True)

    # Sao chép file
    ten_file = os.path.basename(file_goc)
    duong_dan_gui = os.path.join(thu_muc_gui, ten_file)
    shutil.copy2(file_goc, duong_dan_gui)

    # Lưu hash vào file đính kèm
    file_hash = os.path.join(thu_muc_gui, ten_file + ".sha512")
    with open(file_hash, 'w') as f:
        f.write(hash_goc)

    print(f"\n  [2] Đóng gói và gửi đi:")
    print(f"      🖼️  Ảnh      : {duong_dan_gui}")
    print(f"      🔑 File hash : {file_hash}")
    print("      📦 Gói tin gửi gồm: ảnh dữ liệu + file hash SHA-512")
    print(f"\n  ✅ Gửi thành công!")

    return duong_dan_gui, file_hash, hash_goc


# ══════════════════════════════════════════════
#  GIẢ LẬP ĐƯỜNG TRUYỀN MẠNG
# ══════════════════════════════════════════════

def duong_truyen_mang(duong_dan_gui: str, co_tan_cong: bool):
    """
    Mô phỏng đường truyền mạng:
      - Bình thường : ảnh giữ nguyên
      - Có tấn công : kẻ xấu chèn thêm dữ liệu vào ảnh
    """
    print("\n" + "═" * 60)
    print("🌐  ĐƯỜNG TRUYỀN MẠNG")
    print("═" * 60)

    if co_tan_cong:
        print("\n  ⚠️  Phát hiện kẻ tấn công MitM (Man-in-the-Middle)!")
        print("      Đang chèn dữ liệu giả vào ảnh...")
        with open(duong_dan_gui, 'ab') as f:
            f.write(os.urandom(16))          # chèn 16 byte ngẫu nhiên
        print("      💀 Ảnh đã bị chỉnh sửa trên đường truyền!")
    else:
        print("\n  ✅ Đường truyền an toàn — ảnh giữ nguyên.")


# ══════════════════════════════════════════════
#  PHÍA NGƯỜI NHẬN
# ══════════════════════════════════════════════

def nguoi_nhan(duong_dan_nhan: str, file_hash: str):
    """
    Người nhận:
      1. Đọc hash gốc từ file .sha512
      2. Tự tính hash của ảnh nhận được
      3. So sánh → kết luận toàn vẹn hay không
    """
    print("\n" + "═" * 60)
    print("📥  NGƯỜI NHẬN")
    print("═" * 60)

    print(f"\n  [1] Nhận gói tin:")
    print(f"      🖼️  Ảnh nhận : {duong_dan_nhan}")
    print(f"      🔑 File hash : {file_hash}")

    # Đọc hash gốc
    with open(file_hash, 'r') as f:
        hash_goc = f.read().strip()

    # Tính hash ảnh nhận được
    hash_nhan = tinh_hash(duong_dan_nhan)
    kich_thuoc = os.path.getsize(duong_dan_nhan)

    print(f"\n  [2] Đọc hash gốc từ file đính kèm:")
    hien_thi_hash("Hash gốc  (người gửi)", hash_goc)

    print(f"\n  [3] Tính lại hash của ảnh nhận được:")
    print(f"      Tên ảnh   : {os.path.basename(duong_dan_nhan)}")
    print(f"      Kích thước: {kich_thuoc:,} bytes")
    hien_thi_hash("Hash nhận (ảnh thực)", hash_nhan)

    print(f"\n  [4] Xác thực tính toàn vẹn:")
    if hash_goc == hash_nhan:
        print("      ✅ ẢNH TOÀN VẸN — an toàn để sử dụng!")
        return True
    else:
        so_khac = dem_ky_tu_hash_khac_nhau(hash_goc, hash_nhan)
        print("      ❌ ẢNH ĐÃ BỊ THAY ĐỔI — không tin cậy!")
        print(f"      ⚠️  Số ký tự hash khác nhau: {so_khac}/128")
        print("      🚫 Hủy ảnh, yêu cầu gửi lại!")
        return False


# ══════════════════════════════════════════════
#  CHƯƠNG TRÌNH CHÍNH
# ══════════════════════════════════════════════

def chay_demo(co_tan_cong: bool):
    kich_ban = "CÓ TẤN CÔNG MitM" if co_tan_cong else "BÌNH THƯỜNG"
    print(f"\n{'★'*60}")
    print(f"  KỊCH BẢN: {kich_ban}")
    print(f"{'★'*60}")
    print("  Luồng xử lý: Người gửi -> Gửi ảnh + hash -> Đường truyền -> Người nhận -> Xác thực toàn vẹn")

    FILE_GOC     = tim_anh_mau()
    THU_MUC_GUI  = "goi_tin_gui"

    print("\n  [Chuẩn bị] Chọn ảnh mẫu để gửi:")
    print(f"  🖼️  Ảnh được chọn: '{FILE_GOC}' ({os.path.getsize(FILE_GOC):,} bytes)")

    # Người gửi xử lý
    duong_dan_gui, file_hash, _ = nguoi_gui(FILE_GOC, THU_MUC_GUI)

    # Đường truyền mạng (có thể bị tấn công)
    duong_truyen_mang(duong_dan_gui, co_tan_cong)

    # Người nhận kiểm tra
    ket_qua = nguoi_nhan(duong_dan_gui, file_hash)

    # Dọn dẹp thư mục gửi mô phỏng
    shutil.rmtree(THU_MUC_GUI, ignore_errors=True)

    return ket_qua


# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════╗")
    print("║   MÔ PHỎNG GỬI/NHẬN FILE + XÁC THỰC SHA-512        ║")
    print("╚══════════════════════════════════════════════════════╝")

    # Kịch bản 1: Truyền file bình thường
    chay_demo(co_tan_cong=False)

    print("\n\n")

    # Kịch bản 2: Bị tấn công Man-in-the-Middle
    chay_demo(co_tan_cong=True)
