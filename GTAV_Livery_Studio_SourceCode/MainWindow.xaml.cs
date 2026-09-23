using System;
using System.Diagnostics;
using System.IO;
using System.Media;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Microsoft.Win32;
using CodeWalker.GameFiles;

namespace GTAVLiveryStudio
{
    public partial class MainWindow : Window
    {
        private string? selectedFilePath = null;
        private string? lastGeneratedPreview = null;
        private string? lastOutputDir = null;

        private readonly string blenderPath = @"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe";

        public enum ResultStatus { Idle, Processing, Success, Error }

        public MainWindow()
        {
            InitializeComponent();
            SetResultBox(ResultStatus.Idle, "SẴN SÀNG NHẬN FILE", "Kéo thả file .yft hoặc .yft.xml của xe vào ô bên trái để bắt đầu.");
            Log("Phần mềm đã sẵn sàng. Hãy kéo thả file .yft hoặc .yft.xml của xe vào ô bên trên để bắt đầu.");
        }

        #region Embedded Script Loader (Bảo mật mã nguồn .py)
        private string GetEmbeddedPythonScript()
        {
            var assembly = System.Reflection.Assembly.GetExecutingAssembly();
            string[] names = assembly.GetManifestResourceNames();
            string? targetName = null;
            foreach (var n in names)
            {
                if (n.EndsWith("Auto_Export_UV_Template.py", StringComparison.OrdinalIgnoreCase))
                {
                    targetName = n;
                    break;
                }
            }

            if (targetName != null)
            {
                using Stream? stream = assembly.GetManifestResourceStream(targetName);
                if (stream != null)
                {
                    using StreamReader reader = new StreamReader(stream, Encoding.UTF8);
                    return reader.ReadToEnd();
                }
            }

            // Dự phòng tìm file ngoài nếu đang trong môi trường Debug
            string local = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Auto_Export_UV_Template.py");
            if (File.Exists(local)) return File.ReadAllText(local, Encoding.UTF8);

            throw new FileNotFoundException("Không tìm thấy mã kịch bản trích xuất UV trong tài nguyên đóng gói!");
        }
        #endregion

        #region Drag and Drop & Browse
        private void pnlDrop_DragOver(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
                pnlDrop.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#a6e3a1")!;
                pnlDrop.Background = (Brush)new BrushConverter().ConvertFrom("#252538")!;
            }
            e.Handled = true;
        }

        private void pnlDrop_DragLeave(object sender, DragEventArgs e)
        {
            pnlDrop.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#89b4fa")!;
            pnlDrop.Background = (Brush)new BrushConverter().ConvertFrom("#1e1e2e")!;
            e.Handled = true;
        }

        private void pnlDrop_Drop(object sender, DragEventArgs e)
        {
            pnlDrop.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#89b4fa")!;
            pnlDrop.Background = (Brush)new BrushConverter().ConvertFrom("#1e1e2e")!;

            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[]? files = (string[]?)e.Data.GetData(DataFormats.FileDrop);
                if (files != null && files.Length > 0)
                {
                    SelectVehicleFile(files[0]);
                }
            }
            e.Handled = true;
        }

        private void pnlDrop_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            BrowseVehicleFile();
        }

        private void BrowseVehicleFile()
        {
            var ofd = new OpenFileDialog
            {
                Title = "Chọn file mô hình xe GTA V",
                Filter = "GTA V Vehicle Model (*.yft;*.yft.xml;*.xml)|*.yft;*.yft.xml;*.xml|Tất cả tệp (*.*)|*.*"
            };

            if (ofd.ShowDialog() == true)
            {
                SelectVehicleFile(ofd.FileName);
            }
        }

        private void SelectVehicleFile(string filePath)
        {
            if (!File.Exists(filePath)) return;
            selectedFilePath = filePath;
            var fi = new FileInfo(filePath);
            lblSelectedFile.Text = $"📁 {fi.Name} ({(fi.Length / (1024.0 * 1024.0)):F2} MB)";
            SetResultBox(ResultStatus.Idle, "ĐÃ CHỌN FILE XE", $"Sẵn sàng xuất tem cho: {fi.Name}");
            Log($"Đã chọn file: {filePath}");
        }
        #endregion

        #region Status & Result Box Helper
        private void UpdateProgress(double percent, string statusText)
        {
            Dispatcher.Invoke(() =>
            {
                progressBar.Value = Math.Min(100, Math.Max(0, percent));
                lblPercent.Text = $"{(int)progressBar.Value}%";
                lblStatus.Text = statusText;

                if (percent >= 100)
                {
                    lblStatus.Foreground = (Brush)new BrushConverter().ConvertFrom("#10b981")!;
                    lblPercent.Foreground = (Brush)new BrushConverter().ConvertFrom("#10b981")!;
                }
                else
                {
                    lblStatus.Foreground = (Brush)new BrushConverter().ConvertFrom("#06b6d4")!;
                    lblPercent.Foreground = (Brush)new BrushConverter().ConvertFrom("#06b6d4")!;
                }
            });
        }

        private void SetResultBox(ResultStatus status, string title, string detail)
        {
            Dispatcher.Invoke(() =>
            {
                txtResultTitle.Text = title;
                txtResultSub.Text = detail;

                switch (status)
                {
                    case ResultStatus.Idle:
                        txtResultIcon.Text = "ℹ️";
                        txtResultTitle.Foreground = (Brush)new BrushConverter().ConvertFrom("#89b4fa")!;
                        pnlResultBox.Background = (Brush)new BrushConverter().ConvertFrom("#181825")!;
                        pnlResultBox.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#313244")!;
                        break;
                    case ResultStatus.Processing:
                        txtResultIcon.Text = "⚡";
                        txtResultTitle.Foreground = (Brush)new BrushConverter().ConvertFrom("#06b6d4")!;
                        pnlResultBox.Background = (Brush)new BrushConverter().ConvertFrom("#162330")!;
                        pnlResultBox.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#06b6d4")!;
                        break;
                    case ResultStatus.Success:
                        txtResultIcon.Text = "✅";
                        txtResultTitle.Foreground = (Brush)new BrushConverter().ConvertFrom("#10b981")!;
                        pnlResultBox.Background = (Brush)new BrushConverter().ConvertFrom("#12281e")!;
                        pnlResultBox.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#10b981")!;
                        break;
                    case ResultStatus.Error:
                        txtResultIcon.Text = "❌";
                        txtResultTitle.Foreground = (Brush)new BrushConverter().ConvertFrom("#f38ba8")!;
                        pnlResultBox.Background = (Brush)new BrushConverter().ConvertFrom("#2e1820")!;
                        pnlResultBox.BorderBrush = (Brush)new BrushConverter().ConvertFrom("#f38ba8")!;
                        break;
                }
            });
        }
        #endregion

        #region Actions & Export Pipeline
        private async void btnStart_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedFilePath) || !File.Exists(selectedFilePath))
            {
                MessageBox.Show("Vui lòng chọn hoặc kéo thả file xe (.yft hoặc .yft.xml) trước!", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (!File.Exists(blenderPath))
            {
                MessageBox.Show($"Không tìm thấy Blender tại:\n{blenderPath}", "Lỗi Blender", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            btnStart.IsEnabled = false;
            pnlDrop.IsEnabled = false;
            btnOpenFolder.IsEnabled = false;
            btnOpenImage.IsEnabled = false;

            UpdateProgress(5, "⚡ Khởi tạo tiến trình xuất...");
            SetResultBox(ResultStatus.Processing, "ĐANG XỬ LÝ XUẤT UV TEMPLATE...", "CodeWalker & Blender đang bóc tách mô hình 3D...");

            // Lấy độ phân giải người dùng chọn
            int selectedSize = 4096;
            if (cmbResolution.SelectedIndex == 1) selectedSize = 2048;
            else if (cmbResolution.SelectedIndex == 2) selectedSize = 8192;

            bool exportPs = chkPhotoshop.IsChecked == true;
            bool exportPrev = chkPreview.IsChecked == true;
            string psFlag = exportPs ? "1" : "0";
            string prevFlag = exportPrev ? "1" : "0";

            await Task.Run(() =>
            {
                string originalFolder = Path.GetDirectoryName(selectedFilePath)!;
                string targetXmlPath = selectedFilePath;
                string tempDir = Path.Combine(Path.GetTempPath(), "gtav_studio_" + Guid.NewGuid().ToString("N"));
                Directory.CreateDirectory(tempDir);

                try
                {
                    // Trích xuất script Python từ tài nguyên nhúng bên trong file .exe ra thư mục tạm bảo mật
                    string scriptContent = GetEmbeddedPythonScript();
                    string tempScriptPath = Path.Combine(tempDir, "core_engine.py");
                    File.WriteAllText(tempScriptPath, scriptContent, Encoding.UTF8);

                    // Bước 1: Nếu là file .yft nhị phân -> dùng CodeWalker.Core xuất XML tự động
                    if (selectedFilePath.EndsWith(".yft", StringComparison.OrdinalIgnoreCase) && !selectedFilePath.EndsWith(".yft.xml", StringComparison.OrdinalIgnoreCase))
                    {
                        UpdateProgress(15, "⚡ CodeWalker đang giải mã .yft sang XML trên RAM...");
                        Log("[1/3] Phát hiện file .yft nhị phân. Đang gọi CodeWalker.Core giải mã tự động...");

                        byte[] yftBytes = File.ReadAllBytes(selectedFilePath);
                        var yftFile = new YftFile();
                        yftFile.Load(yftBytes);

                        string xmlContent = YftXml.GetXml(yftFile, originalFolder);
                        string generatedXml = Path.Combine(tempDir, Path.GetFileNameWithoutExtension(selectedFilePath) + ".yft.xml");
                        File.WriteAllText(generatedXml, xmlContent, Encoding.UTF8);

                        UpdateProgress(35, "⚡ CodeWalker đã giải mã xong XML...");
                        Log($"[1/3] CodeWalker đã giải mã thành công! Kích thước XML: {(xmlContent.Length / (1024.0 * 1024.0)):F2} MB");
                        targetXmlPath = generatedXml;
                    }
                    else
                    {
                        UpdateProgress(25, "⚡ File đầu vào đã là định dạng XML sẵn sàng...");
                        Log("[1/3] File đầu vào đã là định dạng XML.");
                    }

                    // Bước 2: Gọi Blender trích xuất UV Template trực tiếp ra thư mục của xe (originalFolder)
                    UpdateProgress(40, "⚡ Đang khởi động Blender 5.2...");
                    Log($"[2/3] Đang gọi Blender 5.2 trích xuất kênh UV Livery ra thư mục xe: {originalFolder}...");

                    var psi = new ProcessStartInfo
                    {
                        FileName = blenderPath,
                        Arguments = $"--background --python \"{tempScriptPath}\" -- \"{targetXmlPath}\" \"{originalFolder}\" {selectedSize} {psFlag} {prevFlag}",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        StandardOutputEncoding = Encoding.UTF8,
                        StandardErrorEncoding = Encoding.UTF8,
                        CreateNoWindow = true
                    };

                    using (var proc = Process.Start(psi))
                    {
                        if (proc != null)
                        {
                            proc.OutputDataReceived += (s, ev) =>
                            {
                                if (!string.IsNullOrWhiteSpace(ev.Data))
                                {
                                    string line = ev.Data;
                                    if (line.Contains("[Buoc 1")) UpdateProgress(50, "⚡ Blender đang nạp dữ liệu xe 3D...");
                                    else if (line.Contains("[Buoc 2")) UpdateProgress(65, "⚡ Blender đang lọc thân vỏ và UV Livery...");
                                    else if (line.Contains("[Buoc 3")) UpdateProgress(80, "⚡ Blender đang bóc tách đường nét UV...");
                                    else if (line.Contains("[Buoc 4")) UpdateProgress(90, "⚡ Blender đang vẽ và kết xuất file ảnh 1:1...");

                                    if (line.Contains("[Buoc") || line.Contains("THANH CONG") || line.Contains("HOAN TAT") || line.Contains("THONG BAO") || line.Contains(">>>"))
                                    {
                                        Log(line);
                                    }
                                }
                            };
                            proc.BeginOutputReadLine();
                            proc.WaitForExit();
                        }
                    }

                    UpdateProgress(95, "⚡ Đang kiểm tra và nạp ảnh mẫu kết quả...");

                    // Bước 3: Tìm file kết quả trong chính thư mục xe gốc
                    string vehicleName = Path.GetFileName(selectedFilePath).Replace(".yft.xml", "").Replace(".xml", "").Replace(".yft", "");
                    string previewPng = Path.Combine(originalFolder, $"{vehicleName}_UV_Preview.png");
                    string photoshopPng = Path.Combine(originalFolder, $"{vehicleName}_UV_Template_Photoshop.png");

                    lastOutputDir = originalFolder;
                    if (File.Exists(previewPng))
                    {
                        lastGeneratedPreview = previewPng;
                    }
                    else if (File.Exists(photoshopPng))
                    {
                        lastGeneratedPreview = photoshopPng;
                    }
                    else
                    {
                        lastGeneratedPreview = null;
                    }

                    if (!string.IsNullOrEmpty(lastGeneratedPreview) && File.Exists(lastGeneratedPreview))
                    {
                        Log($"[3/3] Xuất file thành công tại thư mục xe: {lastGeneratedPreview}");
                        if (File.Exists(photoshopPng))
                        {
                            Log($"[3/3] Bản Photoshop: {photoshopPng}");
                        }

                        Dispatcher.Invoke(() =>
                        {
                            try
                            {
                                var bitmap = new BitmapImage();
                                bitmap.BeginInit();
                                bitmap.CacheOption = BitmapCacheOption.OnLoad;
                                bitmap.UriSource = new Uri(lastGeneratedPreview);
                                bitmap.EndInit();
                                bitmap.Freeze();

                                imgPreview.Source = bitmap;
                                pnlPlaceholder.Visibility = Visibility.Collapsed;
                            }
                            catch (Exception imgEx)
                            {
                                Log($"[CẢNH BÁO] Không thể nạp ảnh xem trước: {imgEx.Message}");
                            }

                            btnOpenFolder.IsEnabled = true;
                            btnOpenImage.IsEnabled = true;
                            UpdateProgress(100, "✅ Hoàn tất mỹ mãn (1:1 Template 4K)!");
                            SetResultBox(ResultStatus.Success, "ĐÃ XUẤT XONG HOÀN TẤT!", $"Ảnh 1:1 đã lưu tại thư mục xe: {Path.GetFileName(lastGeneratedPreview)}");
                        });

                        SystemSounds.Asterisk.Play();
                    }
                    else
                    {
                        Log("[CẢNH BÁO] Không tìm thấy file ảnh đầu ra sau khi Blender hoàn thành.");
                        Dispatcher.Invoke(() =>
                        {
                            UpdateProgress(0, "⚠️ Không tìm thấy ảnh đầu ra từ Blender.");
                            SetResultBox(ResultStatus.Error, "ERROR - KHÔNG TÌM THẤY ẢNH", "Blender đã chạy nhưng không tìm thấy file ảnh đầu ra.");
                        });
                    }
                }
                catch (Exception ex)
                {
                    Log($"[LỖI]: {ex.Message}");
                    Dispatcher.Invoke(() =>
                    {
                        UpdateProgress(0, "❌ Đã xảy ra lỗi!");
                        SetResultBox(ResultStatus.Error, "ERROR - XUẤT THẤT BẠI!", ex.Message);
                        MessageBox.Show($"Có lỗi xảy ra: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Error);
                    });
                }
                finally
                {
                    // Tự động xóa sạch toàn bộ thư mục Temp và file script Python tạm ngay lập tức
                    try { Directory.Delete(tempDir, true); } catch { }
                    Dispatcher.Invoke(() =>
                    {
                        btnStart.IsEnabled = true;
                        pnlDrop.IsEnabled = true;
                    });
                }
            });
        }

        private void btnOpenFolder_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(lastGeneratedPreview) && File.Exists(lastGeneratedPreview))
                {
                    // Mở Explorer và tự động highlight (chọn) file ảnh vừa tạo trong thư mục xe
                    Process.Start("explorer.exe", $"/select,\"{lastGeneratedPreview}\"");
                }
                else if (!string.IsNullOrEmpty(lastOutputDir) && Directory.Exists(lastOutputDir))
                {
                    Process.Start("explorer.exe", $"\"{lastOutputDir}\"");
                }
                else
                {
                    MessageBox.Show("Thư mục chứa xe không tồn tại hoặc chưa chọn file.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Không thể mở thư mục: {ex.Message}", "Lỗi", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void btnOpenImage_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (!string.IsNullOrEmpty(lastGeneratedPreview) && File.Exists(lastGeneratedPreview))
                {
                    Process.Start(new ProcessStartInfo
                    {
                        FileName = lastGeneratedPreview,
                        UseShellExecute = true
                    });
                }
                else
                {
                    MessageBox.Show("Chưa tìm thấy file ảnh gốc hoặc ảnh chưa được tạo.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Không thể mở ảnh bằng trình xem mặc định: {ex.Message}\nBạn có thể bấm nút 'Mở thư mục' để tự chọn ảnh.", "Thông báo", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void Log(string message)
        {
            Dispatcher.Invoke(() =>
            {
                txtLog.AppendText($"[{DateTime.Now:HH:mm:ss}] {message}\n");
                txtLog.ScrollToEnd();
            });
        }
        #endregion
    }
}