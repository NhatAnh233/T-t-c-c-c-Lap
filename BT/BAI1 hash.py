import hashlib

def bam_du_lieu(du_lieu: str):
    """Băm dữ liệu gốc (không sửa) và dữ liệu đã sửa bằng SHA-256 và SHA-512"""
    

    du_lieu_goc = du_lieu
    du_lieu_sua = du_lieu[:-1] + ('A' if du_lieu[-1] != 'A' else 'B')  # Sửa 1 ký tự cuối
    
    print("=" * 70)
    print(f"Dữ liệu GỐC : '{du_lieu_goc}'")
    print(f"Dữ liệu SỬA : '{du_lieu_sua}'  ← chỉ thay 1 ký tự cuối")
    print("=" * 70)

    for ten, du_lieu_test in [("KHÔNG SỬA", du_lieu_goc), ("CÓ SỬA", du_lieu_sua)]:
        print(f"\n📌 Trường hợp: {ten}")
        
        # SHA-256
        sha256 = hashlib.sha256(du_lieu_test.encode('utf-8')).hexdigest()
        # SHA-512
        sha512 = hashlib.sha512(du_lieu_test.encode('utf-8')).hexdigest()
        
        print(f"  SHA-256 ({len(sha256)*4} bit): {sha256}")
        print(f"  SHA-512 ({len(sha512)*4} bit): {sha512}")

    print("\n" + "=" * 70)
    print("📊 SO SÁNH — thay 1 ký tự, hash thay đổi hoàn toàn:")
    
    # So sánh từng thuật toán
    for algo in ['sha256', 'sha512']:
        h_goc = getattr(hashlib, algo)(du_lieu_goc.encode()).hexdigest()
        h_sua = getattr(hashlib, algo)(du_lieu_sua.encode()).hexdigest()
        khac_nhau = sum(c1 != c2 for c1, c2 in zip(h_goc, h_sua))
        phan_tram = khac_nhau / len(h_goc) * 100
        print(f"\n  {algo.upper()}:")
        print(f"    Gốc : {h_goc[:32]}...")
        print(f"    Sửa : {h_sua[:32]}...")
        print(f"    → Số ký tự khác nhau: {khac_nhau}/{len(h_goc)} ({phan_tram:.1f}%)")

# Chạy thử
bam_du_lieu("KIET")