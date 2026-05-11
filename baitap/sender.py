import requests, base64
from flask import Flask, request, jsonify, render_template_string
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

app = Flask(__name__)
keys = {"priv": None, "pub": None}

# ==========================================
# KHU VỰC CÀI ĐẶT IP 
# Mặc định đang để chạy chung trên 1 máy (localhost:5001)
RECEIVER_URL = "http://127.0.0.1:5001/receive"
# ==========================================

HTML_SENDER = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><title>Alice - Sender App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #1e1b4b; overflow-x: hidden; color: #fff;}
        .glass-card { background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); border: 1px solid rgba(255, 255, 255, 0.15); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .blob { position: absolute; filter: blur(90px); z-index: -1; opacity: 0.7; animation: float 10s infinite alternate ease-in-out; border-radius: 50%; }
        .blob-1 { top: -5%; left: 0%; width: 450px; height: 450px; background: #ec4899; } 
        .blob-2 { bottom: 0%; right: -5%; width: 400px; height: 400px; background: #f43f5e; animation-delay: -3s;} 
        .blob-3 { top: 30%; left: 30%; width: 350px; height: 350px; background: #eab308; animation-delay: -6s;} 
        @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(-40px, 40px) scale(1.15); } }
        .btn-outline { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3); transition: 0.3s;}
        .btn-outline:hover { background: rgba(255,255,255,0.2); transform: translateY(-2px);}
        .btn-gradient { background: linear-gradient(135deg, #f43f5e, #ec4899, #8b5cf6); background-size: 200% 200%; transition: all 0.4s ease; }
        .btn-gradient:hover { background-position: right center; transform: translateY(-3px); box-shadow: 0 10px 25px rgba(236, 72, 153, 0.5); }
        .input-glass { background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.1); color: #fff; transition: 0.3s; }
        .input-glass:focus { outline: none; border-color: #ec4899; box-shadow: 0 0 15px rgba(236, 72, 153, 0.3); background: rgba(0,0,0,0.4); }
    </style>
</head>
<body class="min-h-screen relative flex items-center justify-center p-6">
    <div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div>
    <div class="max-w-3xl w-full">
        <div class="glass-card rounded-3xl overflow-hidden relative">
            <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h2 class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-rose-400">
                    <i class="fa-solid fa-paper-plane mr-2 text-pink-400"></i> MÁY GỬI (ALICE)
                </h2>
                <div class="text-xs font-mono text-white/50 flex items-center">
                    <i class="fa-solid fa-link mr-1"></i> Auto-connect Mode
                </div>
            </div>
            <div class="p-8 space-y-6">
                <button onclick="genKeys()" class="btn-outline w-full py-4 rounded-xl font-bold tracking-wide flex justify-center items-center">
                    <div class="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent text-lg"><i class="fa-solid fa-key mr-2"></i> 1. TẠO CẶP KHÓA RSA 2048</div>
                </button>
                
                <div class="space-y-2 mt-4">
                    <label class="block text-xs font-bold uppercase tracking-wide text-pink-300 ml-1">Văn bản cần ký</label>
                    <textarea id="msg" class="w-full p-5 rounded-xl input-glass h-36 resize-none text-base">Chào Bob, đây là thông điệp bí mật từ hệ thống mới của Alice!</textarea>
                </div>
                <button onclick="send()" class="btn-gradient w-full py-4 rounded-2xl text-white font-bold text-lg tracking-wide mt-2">
                    <i class="fa-solid fa-file-signature mr-2"></i> 2. KÝ ĐIỆN TỬ & GỬI TỰ ĐỘNG
                </button>
            </div>
        </div>
    </div>
    
    <script>
        const UIConfig = { background: 'rgba(30, 27, 75, 0.95)', color: '#fff', backdrop: 'rgba(0,0,0,0.6) backdrop-blur-sm' };
        
        async function genKeys() {
            Swal.fire({ ...UIConfig, title: 'Đang khởi tạo...', didOpen: () => Swal.showLoading() });
            await fetch('/gen_keys');
            Swal.fire({ ...UIConfig, icon: 'success', title: 'Hoàn tất', text: 'Khóa RSA đã được lưu vào bộ nhớ đệm.', confirmButtonColor: '#ec4899' });
        }
        
        async function send() {
            const msg = document.getElementById('msg').value;
            Swal.fire({ ...UIConfig, title: 'Đang mã hóa & gửi...', didOpen: () => Swal.showLoading() });
            
            try {
                const res = await fetch('/send_action', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg}) // Chỉ gửi duy nhất nội dung
                });
                const data = await res.json();
                
                if(data.status === 'error') {
                    Swal.fire({ ...UIConfig, icon: 'warning', title: 'Quên tạo khóa!', text: 'Bạn phải nhấn TẠO CẶP KHÓA trước.', confirmButtonColor: '#f59e0b' });
                } else if(data.status === 'ok') {
                    Swal.fire({ ...UIConfig, icon: 'success', title: 'Gửi thành công', text: 'Đã truyền dữ liệu tới máy nhận!', confirmButtonColor: '#10b981' });
                } else {
                    throw new Error("Lỗi mạng");
                }
            } catch (e) {
                Swal.fire({ ...UIConfig, icon: 'error', title: 'Mất kết nối', text: 'Hãy chắc chắn file receiver.py đang chạy.', confirmButtonColor: '#ef4444' });
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_SENDER)

@app.route('/gen_keys')
def gen_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    keys['priv'] = private_key
    keys['pub'] = private_key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')
    return jsonify({"status": "ok"})

@app.route('/send_action', methods=['POST'])
def send_action():
    data = request.json
    if not keys['priv']: return jsonify({"status": "error"}), 400
    
    sig = keys['priv'].sign(data['message'].encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())
    payload = { "message": data['message'], "signature": base64.b64encode(sig).decode('utf-8'), "public_key": keys['pub'] }
    
    try:
        # Sử dụng biến URL cố định đã thiết lập sẵn ở trên cùng code
        requests.post(RECEIVER_URL, json=payload, timeout=5)
        return jsonify({"status": "ok"})
    except:
        return jsonify({"status": "fail"})

if __name__ == '__main__':
    app.run(port=5000)