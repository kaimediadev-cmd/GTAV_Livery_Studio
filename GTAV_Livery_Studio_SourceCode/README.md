# 🚗 GTA V Livery Template Studio - C# WPF (XAML) .NET 8

Dự án này sử dụng công nghệ **WPF (XAML)** hiện đại trên nền tảng **.NET 8**, mang lại giao diện Dark Theme phong cách Windows 11 Fluent, bo tròn mượt mà và hỗ trợ hoàn hảo bộ **Visual Studio XAML Designer**.

---

## 📂 Cấu trúc thư mục mã nguồn:
- **`GTAV_Livery_Studio.slnx`**: File Solution XML thế hệ mới nhất của Visual Studio 2022.
- **`GTAV_Livery_Studio.sln`**: File Solution kinh điển (tương thích mọi phiên bản Visual Studio).
- **`MainWindow.xaml`**: Giao diện đồ họa vector XAML (Dark Theme, bo góc, hiệu ứng Hover, Drop Zone viền nét đứt, khung xem trước ảnh).
- **`MainWindow.xaml.cs`**: Xử lý logic sự kiện, Kéo & Thả (Drag & Drop), giải mã binary `.yft` bằng `CodeWalker.Core.dll`, gọi Blender 5.2 chạy ngầm và hiển thị ảnh.
- **`App.xaml` & `App.xaml.cs`**: Điểm khởi động ứng dụng và bộ tài nguyên màu sắc toàn cục.
- **`Auto_Export_UV_Template.py`**: Script kết hợp Blender 5.2 và Sollumz để bóc tách kênh `UVMap 1`. File này được cấu hình **`<EmbeddedResource>`** nhúng ngầm trực tiếp vào nhị phân file `.exe`, không xuất hiện lộ thiên ra ngoài thư mục phân phối để chống lộ và bảo mật mã nguồn.
- **`Libs/`**: Thư mục chứa các DLL phụ thuộc (`CodeWalker.Core.dll`, `SharpDX*.dll`) để trình biên dịch đóng gói tất cả vào 1 file `.exe` duy nhất.
- **`GTAV_Livery_Studio.csproj`**: File cấu hình dự án C# WPF .NET 8 (kích hoạt chế độ `PublishSingleFile`).

---

## 🎨 Cách mở và kéo-thả thiết kế trong Visual Studio:
1. Nhấp đúp vào **`GTAV_Livery_Studio.slnx`** (hoặc `GTAV_Livery_Studio.sln`).
2. Trong cửa sổ **Solution Explorer** bên phải, nhấp đúp vào **`MainWindow.xaml`**.
3. Cửa sổ **Visual Studio XAML Designer** sẽ mở ra:
   - Nửa trên là màn hình xem trước giao diện trực quan (Visual Preview).
   - Nửa dưới là mã XAML trực tiếp. Bác sửa đến đâu thì giao diện tự động cập nhật ngay tức thì (Hot Reload / Live Preview).
   - Có thể dùng **Toolbox** kéo thả thêm controls, hoặc dùng bảng **Properties (F4)** để chỉnh màu sắc, bo góc `CornerRadius`, kích thước...
4. Bấm **F5** (hoặc `Ctrl + F5`) để chạy thử và kiểm tra ứng dụng!