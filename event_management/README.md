## 1. Yêu cầu

- Python 3.11+
- MySQL Server đang chạy (local hoặc Docker)

## 2. Cài đặt

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## 3. Cấu hình môi trường

```bash
cp .env.example .env
```


Tạo database MySQL trước khi chạy app:

```sql
CREATE DATABASE event_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 4. Khởi tạo bảng

```bash
python scripts/create_tables.py
```

## 5. Chạy server

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 6. Danh sách API đã build (chỉ phần Bắt buộc)

### Authentication
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/auth/register` | Đăng ký tài khoản, hash password bằng bcrypt |
| POST | `/auth/login` | Đăng nhập theo chuẩn OAuth2 Password Flow (form-data: `username`=email, `password`) |

### User
| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/users/me` | Thông tin bản thân (không lộ password_hash) |
| GET | `/users` | Danh sách user — chỉ Admin, hỗ trợ search + filter is_active |

### Event
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/events` | Tạo sự kiện, người tạo tự động là Owner |
| GET | `/events` | Danh sách sự kiện của tôi, hỗ trợ search theo tên |
| GET | `/events/{event_id}` | Chi tiết sự kiện — chỉ thành viên mới xem được |
| PATCH | `/events/{event_id}` | Cập nhật sự kiện — chỉ Owner |
| DELETE | `/events/{event_id}` | Xoá sự kiện — chỉ Owner (xoá thật, không phải soft delete) |

### Event Member
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/events/{event_id}/members` | Thêm thành viên — chỉ Owner |
| GET | `/events/{event_id}/members` | Danh sách thành viên |
| DELETE | `/events/{event_id}/members/{user_id}` | Xoá thành viên — chỉ Owner, không xoá được Owner cuối cùng |

### Event Task
| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/events/{event_id}/event-tasks` | Tạo công việc — bất kỳ thành viên nào cũng tạo được |
| GET | `/events/{event_id}/event-tasks` | Danh sách công việc, filter status/priority/assignee, search, phân trang, sort |
| GET | `/event-tasks/{task_id}` | Chi tiết công việc — kiểm tra user thuộc sự kiện |
| PATCH | `/event-tasks/{task_id}` | Cập nhật — chỉ Owner hoặc Assignee, không ghi đè field không gửi lên |
| DELETE | `/event-tasks/{task_id}` | Xoá — chỉ Owner hoặc Assignee |

## 7. Luồng test nhanh trên Swagger UI

1. `POST /auth/register` — tạo tài khoản mới.
2. `POST /auth/login` — đây là **form-data**, không phải JSON. Trên Swagger UI,
   bấm "Try it out", điền field `username` = email vừa đăng ký, `password` =
   mật khẩu, để trống các field khác. Nhận về `access_token`.
3. Bấm nút **Authorize** (góc trên bên phải `/docs`), dán `access_token` vào.
4. `GET /users/me` — kiểm tra thông tin cá nhân.
5. `POST /events` — tạo sự kiện, bạn tự động là OWNER.
6. `POST /events/{event_id}/members` — thêm thành viên khác vào sự kiện.
7. `GET /events/{event_id}` — chỉ member mới xem được (thử token của user không phải member để thấy lỗi 403).
8. `POST /events/{event_id}/event-tasks` — tạo công việc cho sự kiện, có thể gán `assignee_id`.
9. `PATCH /event-tasks/{task_id}` — thử cập nhật status bằng token của Assignee, rồi thử bằng token của Member khác để thấy lỗi 403.

Xem đầy đủ các case cần test tại `docs/test_checklist.md`.

## 8. Cấu trúc thư mục

```
event_management/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── event.py
│   │   └── event_task.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── token.py
│   │   ├── event.py
│   │   └── event_task.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── event.py
│   │   └── event_task.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── event_service.py
│   │   └── event_task_service.py
│   └── dependencies/
│       └── auth.py
├── scripts/
│   └── create_tables.py
├── docs/
│   └── test_checklist.md
├── .env.example
├── requirements.txt
└── README.md
```

## 9. Ghi chú so với bản đầy đủ


- Không có `POST /auth/refresh` — token hết hạn phải đăng nhập lại.
- Không có rate limit chống brute-force cho `/auth/login`.
- Không có Activity log (bảng `activity_logs`).
- Không có Soft delete — `DELETE /events/{event_id}` xoá thật khỏi database, không thể khôi phục.
- Không có Comment, Attachment cho Event Task.

## 10. Permission matrix — Event Task

| Hành động | Owner sự kiện | Member thường | Assignee của task |
|---|---|---|---|
| Tạo task | ✅ | ✅ | — |
| Xem danh sách/chi tiết task | ✅ | ✅ | ✅ |
| Cập nhật task | ✅ (mọi task) | ❌ | ✅ (chỉ task của mình) |
| Xoá task | ✅ (mọi task) | ❌ | ✅ (chỉ task của mình) |
| Được gán làm assignee | phải là thành viên sự kiện | phải là thành viên sự kiện | — |
