# 🚗 GTA V Livery Template Studio

**GTA V Livery Template Studio** là phần mềm chuyên dụng hỗ trợ các modder trích xuất tem xe (UV Layout Template) chất lượng cao **1:1 (4K / 8K / 2K)** trực tiếp từ file mô hình `.yft` hoặc `.yft.xml` của Grand Theft Auto V.

Giao diện được xây dựng bằng công nghệ **C# WPF (XAML) .NET 8** theo phong cách **Windows 11 Fluent Dark Theme**, kết hợp cùng sức mạnh bóc tách 3D từ **CodeWalker.Core** và **Blender 5.2 (Sollumz)**.

---

## ✨ Tính Năng Nổi Bật

- 🏎️ **Kéo & Thả (Drag & Drop) siêu tiện lợi:** Kéo trực tiếp file `.yft` hoặc `.yft.xml` vào phần mềm là tự động nhận diện.
- ⚡ **Giải mã nhị phân trực tiếp trên RAM:** Tích hợp `CodeWalker.Core.dll` để đọc thẳng file `.yft` mà không cần công đoạn convert thủ công rườm rà.
- 🎨 **Lọc UV Thông Minh (Smart UV Filter):**
  - Tự động tách đúng kênh `UVMap 1` (kênh dán tem livery chuyên dụng của GTA V).
  - Loại bỏ các đường seam nối xuyên map (`seam wrapping lines`) và tam giác kẹp biên.
  - Phân tích màu sắc thông minh: Khung lưới đen nền trắng siêu nét cho Photoshop + Khung lưới trắng nền đen tương phản cao cho xem trước.
- 🔒 **Đóng Gói 1 File Duy Nhất (.EXE) & Bảo Mật Mã Nguồn:**
  - Phần mềm được đóng gói thành **1 file `.exe` duy nhất** (~6 MB), không cần cài đặt rườm rà.
  - Mã kịch bản xử lý Python được nhúng ngầm dưới dạng Binary Resource bên trong file `.exe`, tự động dọn sạch thư mục tạm sau khi kết xuất để chống lộ mã nguồn.
- 📊 **Theo Dõi Tiến Trình Thời Gian Thực:**
  - Thanh tiến trình mượt mà từ 0% đến 100%.
  - Bảng Log tự cuộn hiển thị từng bước xử lý.
  - Khung xem trước kết quả trực tiếp tỉ lệ 1:1 ngay trên giao diện.

---

## 📥 Tải Về & Chạy Ngay (Pre-compiled)

Người dùng có thể tải bản chạy trực tiếp (Single-file Portable .EXE) tại mục Releases của dự án:
👉 **[Tải Về Bản Mới Nhất Tại Đây (GitHub Releases)](https://github.com/kaimediadev-cmd/GTAV_Livery_Studio/releases)**

### ⚠️ Yêu Cầu Hệ Thống:
1. **Windows 10/11 64-bit**
2. **.NET 8.0 Desktop Runtime** (hầu hết máy tính hiện nay đều đã có sẵn).
3. **Blender (khuyến nghị 5.2 trở lên)** được cài đặt tại đường dẫn mặc định:
   `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`
4. Đã cài đặt và kích hoạt **Addon Sollumz** trong Blender.

---

## 🛠️ Hướng Dẫn Biên Dịch Mã Nguồn (Build From Source)

Mã nguồn nằm hoàn toàn trong thư mục **`GTAV_Livery_Studio_SourceCode/`**:

1. **Yêu cầu:** Đã cài **Visual Studio 2022** (với workload *.NET Desktop Development*) hoặc cài **.NET 8 SDK**.
2. **Mở dự án:**
   - Nhấp đúp vào file solution **`GTAV_Livery_Studio_SourceCode/GTAV_Livery_Studio.slnx`** (hoặc `.sln`).
   - Có thể chỉnh sửa giao diện trực quan bằng **Visual Studio XAML Designer**.
3. **Biên dịch:**
   - Biên dịch bằng Visual Studio 2022 (**Build Solution** - `Ctrl + Shift + B`) hoặc thông qua .NET CLI:
     ```bash
     dotnet build GTAV_Livery_Studio_SourceCode/GTAV_Livery_Studio.csproj -c Release
     ```

---

## 📢 Thông Tin & Đóng Góp

- Phát triển & Đóng gói bởi: **SonixGTA Mods**
- Mọi góp ý hoặc phản hồi vui lòng gửi về: **Fanpage SonixGTA Mods**
- *Lưu ý:* Công cụ được phát triển phi thương mại nhằm phục vụ cộng đồng modder GTA V. Một số dòng xe nguyên bản của Rockstar Games có thể sử dụng cấu trúc nén đặc thù hoặc không hỗ trợ tem livery.
