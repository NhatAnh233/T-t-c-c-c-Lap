from flask import Flask, request, jsonify, render_template_string
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64

app = Flask(__name__)

# ==========================================
# 1. GIAO DIỆN WEB HIỆN ĐẠI (Tailwind CSS + SweetAlert2)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Phỏng Chữ Ký Số RSA</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Tùy chỉnh thanh cuộn cho khu vực hiển thị key */
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
    </style>
</head>
<body class="bg-slate-100 font-sans text-slate-800 antialiased min-h-screen pb-12">

    <div class="max-w-4xl mx-auto pt-10 px-4">
        <div class="text-center mb-10">
            <h1 class="text-3xl font-extrabold text-slate-900 tracking-tight sm:text-4xl">
                <i class="fa-solid fa-shield-halved text-blue-600 mr-2"></i>Mô Phỏng Chữ Ký Số RSA
            </h1>
            <p class="mt-3 text-lg text-slate-500">Trải nghiệm quá trình tạo khóa, ký thông điệp và xác minh bảo mật.</p>
        </div>

        <div class="space-y-8">
            
            <div class="bg-white rounded-2xl shadow-lg border-t-4 border-blue-500 overflow-hidden transition-all hover:shadow-xl">
                <div class="px-6 py-5 border-b border-slate-100 bg-slate-50/50">
                    <h3 class="text-xl font-bold text-blue-700 flex items-center">
                        <i class="fa-solid fa-user-lock mr-3 text-2xl"></i> Người Gửi (Alice)
                    </h3>
                </div>
                <div class="p-6">
                    <button onclick="generateKeys()" class="w-full sm:w-auto px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors duration-200 flex items-center justify-center">
                        <i class="fa-solid fa-key mr-2"></i> 1. Tạo Cặp Khóa RSA
                    </button>
                    
                    <div id="keys-display" class="hidden mt-6 space-y-4">
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-1">Khóa Bí Mật (Private Key) - Giữ kín:</label>
                            <div class="bg-slate-900 text-emerald-400 font-mono text-xs p-4 rounded-lg overflow-x-auto scrollbar-hide shadow-inner" id="priv-key"></div>
                        </div>
                        <div>
                            <label class="block text-sm font-semibold text-slate-700 mb-1">Khóa Công Khai (Public Key) - Công bố:</label>
                            <div class="bg-slate-900 text-blue-400 font-mono text-xs p-4 rounded-lg overflow-x-auto scrollbar-hide shadow-inner" id="pub-key"></div>
                        </div>
                    </div>

                    <div class="mt-8">
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Thông điệp cần gửi đi:</label>
                        <textarea id="original-message" rows="3" class="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow resize-none shadow-sm text-slate-700">Đây là nội dung tài liệu mật cần được ký số.</textarea>
                    </div>
                    
                    <div class="mt-4 text-right">
                        <button onclick="signMessage()" class="px-6 py-3 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-lg shadow-md transition-colors duration-200">
                            <i class="fa-solid fa-file-signature mr-2"></i> 2. Ký Thông Điệp & Gửi
                        </button>
                    </div>
                </div>
            </div>

            <div class="flex justify-center text-slate-400">
                <i class="fa-solid fa-arrow-down text-3xl animate-bounce"></i>
            </div>

            <div class="bg-white rounded-2xl shadow-lg border-t-4 border-red-500 overflow-hidden relative">
                <i class="fa-solid fa-globe absolute top-10 right-10 text-9xl text-slate-50 opacity-50 pointer-events-none"></i>
                <div class="px-6 py-5 border-b border-slate-100 bg-red-50/30">
                    <h3 class="text-xl font-bold text-red-600 flex items-center">
                        <i class="fa-solid fa-network-wired mr-3 text-xl"></i> Đường Truyền Mạng (Internet)
                    </h3>
                    <p class="text-sm text-red-400 mt-1">Nơi dữ liệu có thể bị đánh chặn hoặc chỉnh sửa bởi tin tặc.</p>
                </div>
                <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Nội dung đang truyền:</label>
                        <textarea id="network-message" rows="5" class="w-full px-4 py-3 border-2 border-red-200 rounded-lg focus:ring-2 focus:ring-red-500 outline-none transition-shadow resize-none shadow-sm text-slate-700 bg-red-50/10"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Chữ ký số đính kèm (Base64):</label>
                        <textarea id="network-signature" rows="5" class="w-full px-4 py-3 border-2 border-red-200 rounded-lg outline-none resize-none shadow-sm text-xs font-mono text-slate-500 bg-slate-50" readonly></textarea>
                    </div>
                </div>
            </div>

            <div class="flex justify-center text-slate-400">
                <i class="fa-solid fa-arrow-down text-3xl animate-bounce"></i>
            </div>

            <div class="bg-white rounded-2xl shadow-lg border-t-4 border-emerald-500 overflow-hidden">
                <div class="px-6 py-5 border-b border-slate-100 bg-emerald-50/50">
                    <h3 class="text-xl font-bold text-emerald-600 flex items-center">
                        <i class="fa-solid fa-user-check mr-3 text-2xl"></i> Người Nhận (Bob)
                    </h3>
                </div>
                <div class="p-6 text-center">
                    <button onclick="verifySignature()" class="w-full sm:w-auto px-8 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow-lg transition-transform duration-200 transform hover:scale-105">
                        <i class="fa-solid fa-shield-check mr-2"></i> 3. Xác Minh Chữ Ký Bằng Khóa Công Khai
                    </button>
                    
                    <div id="verify-result" class="hidden mt-6 p-4 rounded-lg font-bold text-lg border-2">
                        </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        async function generateKeys() {
            Swal.fire({ title: 'Đang tạo khóa...', allowOutsideClick: false, didOpen: () => { Swal.showLoading() } });
            
            try {
                const res = await fetch('/generate_keys', { method: 'POST' });
                const data = await res.json();
                
                document.getElementById('priv-key').innerText = data.private_key;
                document.getElementById('pub-key').innerText = data.public_key;
                
                // Hiệu ứng mở rộng mượt mà
                const keyDisplay = document.getElementById('keys-display');
                keyDisplay.classList.remove('hidden');
                keyDisplay.classList.add('animate-fade-in-down');

                Swal.fire({ icon: 'success', title: 'Hoàn tất!', text: 'Đã tạo cặp khóa RSA 2048-bit.', timer: 1500, showConfirmButton: false });
            } catch (err) {
                Swal.fire({ icon: 'error', title: 'Lỗi', text: 'Không thể tạo khóa.' });
            }
        }

        async function signMessage() {
            const msg = document.getElementById('original-message').value;
            const privKey = document.getElementById('priv-key').innerText;
            
            if (!privKey) {
                return Swal.fire({ icon: 'warning', title: 'Khoan đã!', text: 'Vui lòng nhấn "Tạo Cặp Khóa RSA" trước khi ký.' });
            }
            if (!msg.trim()) {
                return Swal.fire({ icon: 'warning', title: 'Khoan đã!', text: 'Vui lòng nhập nội dung thông điệp.' });
            }

            Swal.fire({ title: 'Đang ký thông điệp...', allowOutsideClick: false, didOpen: () => { Swal.showLoading() } });

            try {
                const res = await fetch('/sign', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, private_key: privKey })
                });
                const data = await res.json();
                
                document.getElementById('network-message').value = msg;
                document.getElementById('network-signature').value = data.signature;
                
                Swal.fire({ icon: 'success', title: 'Đã ký và gửi đi!', text: 'Thông điệp và chữ ký đang nằm trên Đường truyền mạng. Bạn có thể thử làm Hacker bằng cách sửa nội dung.', confirmButtonText: 'Hiểu rồi' });
            } catch (err) {
                Swal.fire({ icon: 'error', title: 'Lỗi', text: 'Không thể ký thông điệp.' });
            }
        }

        async function verifySignature() {
            const msg = document.getElementById('network-message').value;
            const sig = document.getElementById('network-signature').value;
            const pubKey = document.getElementById('pub-key').innerText;
            
            if (!pubKey || !sig) {
                return Swal.fire({ icon: 'warning', title: 'Chưa có dữ liệu!', text: 'Đảm bảo rằng bạn đã tạo khóa và gửi thông điệp xuống đường truyền.' });
            }

            Swal.fire({ title: 'Đang kiểm tra chữ ký...', allowOutsideClick: false, didOpen: () => { Swal.showLoading() } });

            try {
                const res = await fetch('/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, signature: sig, public_key: pubKey })
                });
                const data = await res.json();
                
                const resultEl = document.getElementById('verify-result');
                resultEl.classList.remove('hidden', 'bg-emerald-100', 'border-emerald-500', 'text-emerald-700', 'bg-red-100', 'border-red-500', 'text-red-700');
                
                if (data.verified) {
                    Swal.fire({ icon: 'success', title: 'Hợp Lệ!', text: 'Xác minh thành công.', timer: 1500, showConfirmButton: false });
                    resultEl.classList.add('bg-emerald-100', 'border-emerald-500', 'text-emerald-700');
                    resultEl.innerHTML = '<i class="fa-solid fa-shield-check text-2xl mb-2"></i><br>✅ XÁC MINH THÀNH CÔNG<br><span class="text-sm font-normal">Thông điệp nguyên vẹn, chính xác do Alice gửi.</span>';
                } else {
                    Swal.fire({ icon: 'error', title: 'Cảnh Báo Giả Mạo!', text: 'Chữ ký không khớp với nội dung.', timer: 1500, showConfirmButton: false });
                    resultEl.classList.add('bg-red-100', 'border-red-500', 'text-red-700');
                    resultEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-2xl mb-2 animate-pulse"></i><br>❌ XÁC MINH THẤT BẠI<br><span class="text-sm font-normal">Thông điệp đã bị thay đổi trên đường truyền hoặc chữ ký giả mạo!</span>';
                }
            } catch (err) {
                Swal.fire({ icon: 'error', title: 'Lỗi', text: 'Quá trình xác minh gặp sự cố hệ thống.' });
            }
        }
    </script>
</body>
</html>
"""

# ==========================================
# 2. LOGIC XỬ LÝ MẬT MÃ (Backend Flask giữ nguyên)
# ==========================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate_keys', methods=['POST'])
def api_generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return jsonify({"private_key": priv_pem, "public_key": pub_pem})

@app.route('/sign', methods=['POST'])
def api_sign():
    req = request.json
    message_bytes = req['message'].encode('utf-8')
    priv_pem = req['private_key'].encode('utf-8')

    private_key = serialization.load_pem_private_key(priv_pem, password=None)
    
    signature = private_key.sign(
        message_bytes,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    return jsonify({"signature": sig_b64})

@app.route('/verify', methods=['POST'])
def api_verify():
    req = request.json
    message_bytes = req['message'].encode('utf-8')
    pub_pem = req['public_key'].encode('utf-8')
    
    try:
        sig_bytes = base64.b64decode(req['signature'])
        public_key = serialization.load_pem_public_key(pub_pem)
        
        public_key.verify(
            sig_bytes,
            message_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return jsonify({"verified": True})
    except Exception as e:
        return jsonify({"verified": False, "error": str(e)})

if __name__ == '__main__':
    print("Khởi động server... Truy cập http://127.0.0.1:5000 trên trình duyệt của bạn!")
    app.run(debug=True)