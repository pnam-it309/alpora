# Hướng dẫn bảo trì ALPORA

Tài liệu này là "bản đồ" để một người (hoặc agent) mới vẫn bảo trì được dự án.

## 1. Bản đồ kiến trúc

| Lớp | Thư mục | Vai trò | Quy tắc |
|---|---|---|---|
| Core Python | `poly_shell/core/` | state, IPC, daemon, i18n, resilience | Không import từ `commands/` hay `services/` |
| Services | `poly_shell/services/` | logic nghiệp vụ (organizer, update, storage...) | Mỗi service một file, không đụng UI |
| System/Theming | `poly_shell/system/`, `poly_shell/theming/` | desktop, lockscreen, themes, wallpaper | Mọi thay đổi theme phải rollback được |
| CLI | `poly_shell/commands/` + `cli.py` | lệnh `poly-shell ...` | Chỉ parse đối số rồi gọi service |
| Core QML | `shell/core/` | singleton trạng thái (Session, ThemeState...) | Gọi backend qua `Session.controller` |
| UI | `shell/panels/`, `shell/settings/`, `shell/components/` | giao diện | Màu lấy từ `Session`/`PolyTheme`, xem `AGENTS.md` |
| Phân phối | `install/`, `packaging/`, `.github/workflows/` | cài đặt, AUR, ISO, Pages | Sửa xong phải chạy dry-run |

Luồng chính: QML -> `poly-shell <lệnh>` (hoặc `bin/poly-ipc-fast`) -> `commands/` -> `services|system|theming` -> file trong `~/.config/poly-shell` và `~/.local/state`.

## 2. Quy ước bắt buộc
- Mỗi file nguồn dưới 500 dòng (`tests/test_file_budget.py` chặn). Tách theo trách nhiệm, đăng ký QML mới trong `shell/qmldir`.
- Không hardcode màu/đường dẫn người dùng; UI phải chạy với mọi theme (`docs/architecture/theme-design-contract.md`).
- Thêm chuỗi UI thì thêm key vào cả 4 locale `assets/locales/{en,vi,es,ru}.json` (`test_i18n.py` kiểm tra).
- Không `shell=True`; chạy lệnh ngoài qua `SafeRunner`/allowlist.
- Tính năng mới phải có test trong `tests/`.

## 3. Quy trình hằng ngày
1. `./scripts/setup-git-hooks.sh` một lần (pre-commit chạy Ruff + `./scripts/check`).
2. Làm trên nhánh `feat/...` hoặc `fix/...`, mở PR vào `main`.
3. Trước khi push: `python3 -m unittest discover -s tests < /dev/null` và `/usr/lib/qt6/bin/qmllint -I shell <file.qml>`.
4. Merge khi CI (`CI/CD Pipeline`, SonarCloud) xanh hết.

## 4. Lịch bảo trì định kỳ
- **Hằng tuần:** xem Issues/PR, chạy `poly-shell update check`, xem SonarCloud có issue mới.
- **Hằng tháng:** merge PR Dependabot, rà `known-issues.md`, dọn tag/nhánh cũ.
- **Mỗi quý:** chạy audit bảo mật (`poly-shell security audit`), rà file gần ngưỡng 400 dòng.

## 5. Phát hành
1. Cập nhật `CHANGELOG.md` (mục mới trên cùng) và version trong `packaging/`.
2. Đảm bảo `main` xanh, rồi `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. Kiểm tra workflow AUR/ISO/Pages chạy thành công; kiểm tra `poly-shell update check` thấy bản mới.

## 6. Xử lý sự cố nhanh
| Triệu chứng | Kiểm tra |
|---|---|
| CI đỏ | `gh run list -R pnam-it309/alpora`, xem log job fail đầu tiên |
| SonarCloud fail | thường là hash yếu (MD5), regex backtracking, secret lộ |
| Theme không áp dụng | `poly-shell theme list`, xem `~/.local/state/poly-shell/` và `lockscreen.py` |
| Shell không lên | `quickshell -p shell` xem lỗi QML, chạy `qmllint` |
| Test treo | có test gọi `sudo`; chạy với `< /dev/null` |

## 7. Lộ trình gợi ý
- Ngắn hạn: giữ CI xanh, đưa `shell/demos/web/app.js` (771 dòng) xuống dưới 500.
- Trung hạn: thêm ảnh chụp tự động (`scripts/screenshot.sh`) vào CI cho các panel chính; mở rộng lịch (đồng bộ ICS).
- Dài hạn: bên thứ hai review mọi PR (cập nhật `CODEOWNERS`), tách `poly_shell` thành package pip phát hành riêng.
