# HNHErp — Phần mềm Quản lý Nguồn lực Doanh Nghiệp HNHERP

Frappe HRMS tùy chỉnh cho Công ty Hồng Ngọc Hà.

## Quy tắc

- **Ngôn ngữ UI:** Tiếng Việt. Dùng `__("...")` trong Vue và `_("...")` trong Python.
- **Branch:** `develop`.
- **Không commit** khi chưa được yêu cầu rõ ràng.

## Paths

- App source: `~/Sources/hrms` (symlinked vào `~/frappe-bench/apps/hrms`)
- Bench: `~/frappe-bench`
- Site: `hrms.localhost`

## File quan trọng

| File | Mục đích |
|---|---|
| `hrms/hooks.py` | Branding, app_home=/hrms |
| `frontend/src/views/Login.vue` | Trang đăng nhập |
| `hrms/locale/vi.po` | Bản dịch tiếng Việt |
| `~/frappe-bench/Procfile` | Gunicorn config (dùng wsgi:application) |
| `~/frappe-bench/wsgi.py` | WSGI wrapper bật static file serving |

## Lệnh

```bash
# Server
cd ~/frappe-bench && bench start

# Frontend build
cd ~/Sources/hrms && yarn build

# Clear cache (sau khi sửa vi.po / hooks)
cd ~/frappe-bench/sites && ../env/bin/python -c "
import frappe; frappe.init(site='hrms.localhost'); frappe.connect(); frappe.clear_cache(); frappe.destroy()"
```

## Lưu ý

- **Static assets:** Phải dùng `wsgi.py` wrapper, không dùng `frappe.app:application` trực tiếp (sẽ 404 cho `/assets`).
- **Logo:** Đặt trong `Website Settings.app_logo` (DB) thay vì hook (3 app đăng ký logo, hook order không reliable).
- **app_home:** `/hrms` — workspace "People" không tồn tại trong DB.
- **erpnext compat:** `erpnext/holiday_list.py` có stub `is_half_holiday()` cho hrms develop — **không xóa**.

# gstack

For all web browsing, use the `/browse` skill from gstack. Never use `mcp__claude-in-chrome__*` tools.

Available gstack skills:

- `/office-hours`
- `/plan-ceo-review`
- `/plan-eng-review`
- `/plan-design-review`
- `/design-consultation`
- `/design-shotgun`
- `/design-html`
- `/review`
- `/ship`
- `/land-and-deploy`
- `/canary`
- `/benchmark`
- `/browse`
- `/connect-chrome`
- `/qa`
- `/qa-only`
- `/design-review`
- `/setup-browser-cookies`
- `/setup-deploy`
- `/setup-gbrain`
- `/retro`
- `/investigate`
- `/document-release`
- `/document-generate`
- `/codex`
- `/cso`
- `/autoplan`
- `/plan-devex-review`
- `/devex-review`
- `/careful`
- `/freeze`
- `/guard`
- `/unfreeze`
- `/gstack-upgrade`
- `/learn`
