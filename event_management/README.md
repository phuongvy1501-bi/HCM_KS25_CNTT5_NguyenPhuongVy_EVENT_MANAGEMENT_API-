# Event Management API

FastAPI + SQLAlchemy + MySQL. Bao gồm Tiết 1 (nền tảng), Tiết 2 (Auth & User),
Tiết 3 (Event Management).

## 1. Yêu cầu

- Python 3.11+
- MySQL Server đang chạy (local hoặc Docker)

## 2. Cài đặt

```bash
# Tạo và kích hoạt virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt
```

## 3. Cấu hình môi trường

```bash
cp .env.example .env
```

Mở file `.env` và sửa `DATABASE_URL`, `SECRET_KEY` cho phù hợp với máy của bạn.

Tạo database MySQL trước khi chạy app:

```sql
CREATE DATABASE event_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 4. Khởi tạo bảng

```bash
python scripts/create_tables.py
```

## 5. (Tùy chọn) Seed dữ liệu mẫu

```bash
python scripts/seed_data.py
```

Tài khoản mẫu sau khi seed:

| Email | Password | Role |
|---|---|---|
| admin@example.com | Admin@123 | ADMIN |
| owner@example.com | Owner@123 | USER (owner sự kiện mẫu) |
| member@example.com | Member@123 | USER (member sự kiện mẫu) |

## 6. Chạy server

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 7. Luồng test nhanh trên Swagger UI

1. `POST /auth/register` — tạo tài khoản mới (hoặc dùng tài khoản đã seed).
2. `POST /auth/login` — lấy `access_token` + `refresh_token`.
3. Bấm nút **Authorize** (góc trên bên phải `/docs`), dán `access_token`.
4. `GET /users/me` — kiểm tra thông tin cá nhân (không có `password_hash`).
5. `POST /events` — tạo sự kiện, bạn tự động là OWNER.
6. `POST /events/{event_id}/members` — thêm thành viên khác vào sự kiện.
7. `GET /events/{event_id}` — chỉ member mới xem được (thử bằng token của user không phải member để thấy lỗi 403).
8. `PATCH /events/{event_id}` / `DELETE /events/{event_id}` — chỉ OWNER mới thực hiện được.

## 8. Cấu trúc thư mục

```
event_management/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   └── limiter.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── event_task.py
│   │   └── activity_log.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── token.py
│   │   ├── event.py
│   │   └── event_task.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── event.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── event_service.py
│   │   └── activity_log_service.py
│   └── dependencies/
│       └── auth.py
├── scripts/
│   ├── create_tables.py
│   └── seed_data.py
├── .env.example
├── requirements.txt
└── README.md
```
