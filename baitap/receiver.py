from flask import Flask, request, jsonify, render_template_string
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
import base64

app = Flask(__name__)

received_data = {
    "message": "",
    "signature": "",
    "public_key": "",
    "status": "Chưa có kết nối..."
}

HTML_RECEIVER = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8"><title>Bob - Receiver App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; overflow-x: hidden; color: #fff;}
        .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); }
        .blob { position: absolute; filter: blur(90px); z-index: -1; opacity: 0.6; animation: float 12s infinite alternate ease-in-out; border-radius: 50%; }
        .blob-1 { top: -10%; left: -10%; width: 400px; height: 400px; background: #3b82f6; }
        .blob-2 { bottom: -10%; right: -10%; width: 500px; height: 500px; background: #8b5cf6; animation-delay: -4s;}
        .blob-3 { top: 40%; left: 40%; width: 350px; height: 350px; background: #06b6d4; animation-delay: -8s;}
        @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 50px) scale(1.2); } }
        .btn-modern { background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6); background-size: 200% 200%; transition: all 0.4s ease; }
        .btn-modern:hover { background-position: right center; transform: translateY(-3px); box-shadow: 0 10px 25px rgba(59, 130, 246, 0.5); }
        .data-box { background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.05); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
    </style>
</head>
<body class="min-h-screen relative flex items-center justify-center p-6">
    <div class="blob blob-1"></div><div class="blob blob-2"></div><div class="blob blob-3"></div>
    <div class="max-w-4xl w-full">
        <div class="glass-card rounded-3xl overflow-hidden">
            <div class="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                <h2 class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
                    <i class="fa-solid fa-inbox mr-2 text-cyan-400"></i> MÁY NHẬN (BOB)
                </h2>
                <div class="flex items-center bg-white/10 px-4 py-1.5 rounded-full backdrop-blur-md">
                    <div class="w-2.5 h-2.5 bg-green-400 rounded-full animate-pulse mr-2"></div>
                    <span class="text-sm font-semibold tracking-wide">PORT: 5001</span>
                </div>
            </div>
            <div class="p-8 space-y-6">
                <div class="relative group">
                    <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                    <div class="relative data-box rounded-xl p-5">
                        <label class="block text-xs uppercase tracking-wider text-cyan-300 font-bold mb-3"><i class="fa-solid fa-envelope-open-text mr-1"></i> Nội dung nhận được</label>
                        <div class="text-base font-medium leading-relaxed">{{ data.message or 'Đang chờ tin nhắn...' }}</div>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="data-box rounded-xl p-4">
                        <label class="block text-xs uppercase tracking-wider text-purple-300 font-bold mb-2"><i class="fa-solid fa-fingerprint mr-1"></i> Chữ ký số</label>
                        <textarea class="w-full text-xs font-mono p-3 bg-transparent text-gray-300 h-28 focus:outline-none resize-none" readonly>{{ data.signature }}</textarea>
                    </div>
                    <div class="data-box rounded-xl p-4">
                        <label class="block text-xs uppercase tracking-wider text-blue-300 font-bold mb-2"><i class="fa-solid fa-key mr-1"></i> Khóa công khai SENDER</label>
                        <textarea class="w-full text-xs font-mono p-3 bg-transparent text-gray-300 h-28 focus:outline-none resize-none" readonly>{{ data.public_key }}</textarea>
                    </div>
                </div>
                <button onclick="verify()" class="btn-modern w-full py-4 rounded-2xl text-white font-bold text-lg tracking-wide mt-4">
                    <i class="fa-solid fa-shield-check mr-2"></i> XÁC MINH TOÀN VẸN DỮ LIỆU
                </button>
            </div>
        </div>
    </div>
    <script>
        async function verify() {
            Swal.fire({ title: 'Đang xử lý thuật toán...', background: 'rgba(15, 23, 42, 0.9)', color: '#fff', backdrop: 'rgba(0,0,0,0.6) backdrop-blur-sm', didOpen: () => Swal.showLoading() });
            try {
                const res = await fetch('/verify_action', { method: 'POST' });
                const result = await res.json();
                if(result.verified) {
                    Swal.fire({ icon: 'success', title: 'Hợp Lệ!', text: 'Chữ ký chính xác. Tin nhắn không bị thay đổi.', background: 'rgba(15, 23, 42, 0.95)', color: '#fff', confirmButtonColor: '#3b82f6' });
                } else {
                    Swal.fire({ icon: 'error', title: 'Cảnh Báo!', text: 'Xác minh thất bại! Dữ liệu đã bị giả mạo.', background: 'rgba(15, 23, 42, 0.95)', color: '#ef4444', confirmButtonColor: '#ef4444' });
                }
            } catch (e) {
                Swal.fire({ icon: 'info', title: 'Chưa có dữ liệu', text: 'Chưa nhận được thông điệp nào để xác minh.', background: 'rgba(15, 23, 42, 0.95)', color: '#fff' });
            }
        }
        setInterval(() => { location.reload(); }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_RECEIVER, data=received_data)

@app.route('/receive', methods=['POST'])
def receive():
    global received_data
    received_data = request.json
    return jsonify({"status": "received"}), 200

@app.route('/verify_action', methods=['POST'])
def verify_action():
    try:
        pub_key = serialization.load_pem_public_key(received_data['public_key'].encode('utf-8'))
        sig = base64.b64decode(received_data['signature'])
        msg = received_data['message'].encode('utf-8')
        pub_key.verify(sig, msg, padding.PKCS1v15(), hashes.SHA256())
        return jsonify({"verified": True})
    except:
        return jsonify({"verified": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)