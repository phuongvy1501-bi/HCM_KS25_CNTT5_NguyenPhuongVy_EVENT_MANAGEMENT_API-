# Checklist test API — Event Management API

Dùng file này để test thủ công trên Swagger UI (`/docs`) hoặc Postman.
Với mỗi dòng, tick sau khi đã test và kết quả đúng như mô tả.

## Authentication

| # | Case | Bước test | Kết quả mong đợi |
|---|---|---|---|
| 1 | Đăng ký hợp lệ | POST /auth/register với email mới | 201, trả về user, không có password_hash |
| 2 | Đăng ký email trùng | Đăng ký lại đúng email vừa tạo | 400, error = BAD_REQUEST |
| 3 | Đăng ký password ngắn | password = "123" | 422 (Pydantic validation) |
| 4 | Đăng nhập đúng | POST /auth/login (form-data: username, password) | 200, trả về access_token |
| 5 | Đăng nhập sai password | Sai password | 401, error = UNAUTHORIZED |
| 6 | Đăng nhập email không tồn tại | Email lạ | 401, message giống hệt case 5 (không lộ thông tin) |
| 7 | Gọi API không kèm token | GET /users/me không có header Authorization | 401 |
| 8 | Gọi API với token sai | Header Authorization: Bearer abc123 | 401 |

## User

| # | Case | Bước test | Kết quả mong đợi |
|---|---|---|---|
| 9 | Xem profile bản thân | GET /users/me với token hợp lệ | 200, đúng user đang login |
| 10 | User thường xem danh sách user | GET /users với token role USER | 403, error = FORBIDDEN |
| 11 | Admin xem danh sách user | GET /users với token role ADMIN | 200, trả về danh sách |
| 12 | Search user theo tên | GET /users?search=vy | 200, chỉ trả user khớp |

## Event

| # | Case | Bước test | Kết quả mong đợi |
|---|---|---|---|
| 13 | Tạo sự kiện | POST /events | 201, người tạo là owner |
| 14 | Xem chi tiết khi không phải member | GET /events/{id} bằng token user khác | 403 |
| 15 | Update sự kiện không phải Owner | PATCH /events/{id} bằng token Member | 403 |
| 16 | Update sự kiện không tồn tại | PATCH /events/99999 | 404 |
| 17 | Xóa sự kiện bằng Owner | DELETE /events/{id} | 204 |
| 18 | Tạo sự kiện tên rỗng | POST /events {"name": ""} | 422 |

## Event Member

| # | Case | Bước test | Kết quả mong đợi |
|---|---|---|---|
| 19 | Thêm member hợp lệ | POST /events/{id}/members | 201 |
| 20 | Thêm member với user_id không tồn tại | user_id = 999999 | 404 |
| 21 | Thêm member đã tồn tại | Thêm lại đúng user_id vừa thêm | 400 |
| 22 | Member thường (không phải Owner) thêm thành viên | POST bằng token Member | 403 |
| 23 | Xóa Owner cuối cùng | DELETE .../members/{owner_id} khi chỉ có 1 Owner | 400 |

## Event Task

| # | Case | Bước test | Kết quả mong đợi |
|---|---|---|---|
| 24 | Member tạo task | POST /events/{id}/event-tasks | 201, status mặc định TODO |
| 25 | Giao task cho người ngoài sự kiện | assignee_id không phải member | 400 |
| 26 | Xem task của sự kiện khác (không phải member) | GET /event-tasks/{id} | 403 |
| 27 | Member thường (không phải Owner/Assignee) sửa task | PATCH /event-tasks/{id} | 403 |
| 28 | Assignee tự cập nhật status task của mình | PATCH /event-tasks/{id} {"status": "DONE"} | 200 |
| 29 | Owner xóa task bất kỳ | DELETE /event-tasks/{id} | 204 |
| 30 | Filter theo status + priority cùng lúc | GET /events/{id}/event-tasks?status=TODO&priority=HIGH | 200, đúng kết quả lọc |
| 31 | Search theo title | GET /events/{id}/event-tasks?search=slide | 200 |
| 32 | Phân trang | GET /events/{id}/event-tasks?skip=0&limit=1 | 200, đúng 1 kết quả |
| 33 | Sort theo due_date | GET /events/{id}/event-tasks?sort_by=due_date | 200, đúng thứ tự |

## Format lỗi chung

| # | Case | Kiểm tra |
|---|---|---|
| 34 | Bất kỳ lỗi 400/401/403/404 nào | Response luôn có đủ 6 trường: success, code, message, data, error, timestamp |
| 35 | Lỗi 500 (nếu cố tình gây lỗi) | Không lộ stacktrace, vẫn đúng format 6 trường |

## Cách test nhanh

1. Mở `http://127.0.0.1:8000/docs`
2. Test `/auth/register` → `/auth/login` (nhớ dùng tab "Try it out", điền `username` = email, `password` = mật khẩu — vì đây là form OAuth2, không phải JSON)
3. Copy `access_token` nhận được, bấm nút **Authorize** (góc trên bên phải), dán token vào
4. Lần lượt test các case trong bảng trên
