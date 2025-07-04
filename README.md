# Mô phỏng Bảo mật Ngân hàng

## Giới thiệu

Đây là một dự án mô phỏng hệ thống kiểm tra bảo mật an ninh giao dịch ngân hàng, giúp người dùng rèn luyện kỹ năng phát hiện các giao dịch nguy hiểm thông qua các thao tác xác thực chữ ký số (RSA/SHA), giải mã dữ liệu (AES) và ra quyết định phê duyệt hoặc từ chối giao dịch. Giao diện hiện đại, thân thiện, trực quan, phù hợp cho đào tạo hoặc kiểm thử kiến thức an ninh thông tin.

## Tính năng nổi bật
- **Kiểm tra chữ ký số RSA/SHA**: Xác thực tính toàn vẹn và nguồn gốc giao dịch.
- **Giải mã dữ liệu AES**: Xem thông tin chi tiết giao dịch sau khi xác thực.
- **Ra quyết định phê duyệt/từ chối**: Đánh giá mức độ an toàn của từng giao dịch.
- **Nhiều cấp độ thử thách**: Từ giao dịch hợp lệ, tấn công thay đổi dữ liệu, hỏng mã hóa, đến giả mạo chữ ký.
- **Giao diện web hiện đại**: Responsive, dễ sử dụng, có bảng điểm và thông báo nâng cấp cấp độ.

## Cài đặt
1. **Yêu cầu**:
   - Python 3.8+
   - Các thư viện: `flask`, `flask_socketio`, `pycryptodome`
2. **Cài đặt thư viện**:
   ```bash
   pip install flask flask_socketio pycryptodome
   ```
3. **Khởi tạo dữ liệu và khóa**:
   ```bash
   python generate_keys.py
   python create_sample_data.py
   ```

## Chạy ứng dụng
```bash
python app.py
```
Sau đó truy cập [http://127.0.0.1:5000](http://127.0.0.1:5000) trên trình duyệt.

## Cấu trúc thư mục
```
Bank_Security/
├── app.py                  # Server Flask chính, xử lý logic game
├── generate_keys.py        # Tạo khóa RSA cho khách hàng, ngân hàng, hacker
├── create_sample_data.py   # Sinh dữ liệu giao dịch mẫu cho các cấp độ
├── data/                   # Chứa file khóa AES và các file giao dịch mẫu
├── keys/                   # Chứa các file khóa RSA
├── static/
│   └── style.css           # Giao diện CSS hiện đại
├── templates/
│   └── index.html          # Giao diện web chính
└── utils/
    ├── crypto_utils.py     # Hàm mã hóa, giải mã, ký, xác thực
    └── transaction_utils.py# Hàm tạo giao dịch an toàn
```

## Mô tả các thành phần chính
- **app.py**: Chạy server Flask, quản lý trạng thái game, socket, xử lý các thao tác xác thực, giải mã, quyết định.
- **generate_keys.py**: Tạo khóa RSA cho khách hàng, ngân hàng, hacker (dùng cho các tình huống tấn công).
- **create_sample_data.py**: Sinh dữ liệu giao dịch mẫu cho 3 cấp độ, bao gồm cả các giao dịch bị tấn công (tampering, corruption, impersonation).
- **utils/crypto_utils.py**: Hàm tạo khóa, ký, xác thực chữ ký, mã hóa/giải mã AES.
- **utils/transaction_utils.py**: Hàm tạo gói giao dịch an toàn (mã hóa + ký).
- **templates/index.html**: Giao diện web, có 3 màn hình: bắt đầu, chơi, kết quả. Hỗ trợ thao tác kiểm tra, giải mã, quyết định, xem điểm, lên cấp.
- **static/style.css**: Giao diện hiện đại, responsive, màu sắc rõ ràng, hỗ trợ dark mode.

## Mở rộng & Tùy biến
- Thêm cấp độ mới bằng cách bổ sung dữ liệu vào `create_sample_data.py`.
- Tùy biến giao diện tại `static/style.css` và `templates/index.html`.
- Có thể tích hợp thêm các loại tấn công hoặc thuật toán mã hóa khác trong `utils/`.

## Đóng góp
Mọi ý kiến đóng góp, báo lỗi hoặc đề xuất cải tiến xin gửi qua GitHub hoặc liên hệ trực tiếp với tác giả.

---
**Liên hệ:**
- Minh Quang
- Email: minhquangts2004@gmail.com 
