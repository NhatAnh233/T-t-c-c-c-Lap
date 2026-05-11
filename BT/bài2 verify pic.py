import hashlib
import os

def tinh_hash_file(duong_dan: str) -> str:
    """Tính SHA-512 của một file (đọc theo từng chunk để xử lý file lớn)"""
    sha512 = hashlib.sha512()
    
    with open(duong_dan, 'rb') as f:          # mở file ở chế độ binary
        while chunk := f.read(8192):          # đọc từng 8KB một
            sha512.update(chunk)
    
    return sha512.hexdigest()


def luu_hash(duong_dan_anh: str, duong_dan_hash: str):
    """Tính và lưu hash của file ảnh gốc ra file .txt"""
    hash_goc = tinh_hash_file(duong_dan_anh)
    
    with open(duong_dan_hash, 'w') as f:
        f.write(hash_goc)
    
    print(f"✅ Đã lưu hash gốc của '{duong_dan_anh}'")
    print(f"   SHA-512: {hash_goc[:40]}...{hash_goc[-10:]}")
    print(f"   → Lưu vào: '{duong_dan_hash}'")
    return hash_goc


def kiem_tra_toan_ven(duong_dan_anh: str, duong_dan_hash: str):
    """So sánh hash hiện tại của file với hash đã lưu trước đó"""
    print(f"\n🔍 Đang kiểm tra: '{duong_dan_anh}'")
    
    # Đọc hash gốc đã lưu
    with open(duong_dan_hash, 'r') as f:
        hash_goc = f.read().strip()
    
    # Tính hash hiện tại
    hash_hien_tai = tinh_hash_file(duong_dan_anh)
    
    kich_thuoc = os.path.getsize(duong_dan_anh)
    print(f"   Kích thước file : {kich_thuoc:,} bytes")
    print(f"   Hash gốc        : {hash_goc[:40]}...")
    print(f"   Hash hiện tại   : {hash_hien_tai[:40]}...")
    
    if hash_goc == hash_hien_tai:
        print("   ✅ KẾT QUẢ: File TOÀN VẸN — không bị chỉnh sửa!")
    else:
        print("   ❌ KẾT QUẢ: File ĐÃ BỊ THAY ĐỔI hoặc hỏng!")
        # Đếm số ký tự khác nhau
        khac = sum(c1 != c2 for c1, c2 in zip(hash_goc, hash_hien_tai))
        print(f"   ⚠️  Số ký tự hash khác nhau: {khac}/128")


def gia_lap_chinh_sua_file(duong_dan_anh: str):
    """Giả lập việc file bị chỉnh sửa (thêm 1 byte vào cuối)"""
    with open(duong_dan_anh, 'ab') as f:
        f.write(b'\x00')
    print(f"\n⚠️  Đã giả lập chỉnh sửa file '{duong_dan_anh}' (thêm 1 byte)")


if __name__ == "__main__":
    FILE_ANH  = "file ảnh/z7765671397380_1fc8c8a56bee9b71fbd9467d5eb73be2.jpg"       # đường dẫn file ảnh
    FILE_HASH = "anh_goc.sha512"    # file lưu hash

    print("=" * 60)
    print("  KIỂM TRA TÍNH TOÀN VẸN FILE ẢNH BẰNG SHA-512")
    print("=" * 60)

    # Bước 1: Lưu hash gốc
    print("\n📌 BƯỚC 1 — Lưu hash gốc của file ảnh:")
    luu_hash(FILE_ANH, FILE_HASH)

    # Bước 2: Kiểm tra khi file chưa bị sửa
    print("\n📌 BƯỚC 2 — Kiểm tra file CHƯA bị sửa:")
    kiem_tra_toan_ven(FILE_ANH, FILE_HASH)

    # Bước 4: Kiểm tra lại sau khi bị sửa
    print("\n📌 BƯỚC 4 — Kiểm tra file SAU KHI bị sửa:")
    kiem_tra_toan_ven(FILE_ANH, FILE_HASH)