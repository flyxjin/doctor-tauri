using System;
using System.ComponentModel;
using System.IO;
using System.Net;
using System.Reflection;
using System.Threading;
using System.Windows.Forms;
using System.Xml;

namespace MedicineSystem.Core
{
    public class UpdateInfo
    {
        public string Version { get; set; }
        public string ReleaseDate { get; set; }
        public string DownloadUrl { get; set; }
        public string ChangeLog { get; set; }
        public bool IsUpdateAvailable { get; set; }
        public long FileSize { get; set; }
    }

    public class UpdateChecker
    {
        private static readonly string UpdateUrl = "https://api.github.com/repos/your-repo/medicine-system/releases/latest";
        private static readonly string VersionFile = "version.xml";
        private static readonly string CurrentVersion = "1.0.0";

        public static string GetCurrentVersion()
        {
            return CurrentVersion;
        }

        public static UpdateInfo CheckForUpdate()
        {
            var info = new UpdateInfo
            {
                Version = CurrentVersion,
                IsUpdateAvailable = false
            };

            try
            {
                var localVersionPath = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "MedicineSystem",
                    VersionFile
                );

                if (File.Exists(localVersionPath))
                {
                    var doc = new XmlDocument();
                    doc.Load(localVersionPath);

                    var versionNode = doc.SelectSingleNode("//version");
                    var dateNode = doc.SelectSingleNode("//releaseDate");
                    var urlNode = doc.SelectSingleNode("//downloadUrl");
                    var changeLogNode = doc.SelectSingleNode("//changeLog");
                    var sizeNode = doc.SelectSingleNode("//fileSize");

                    if (versionNode != null)
                        info.Version = versionNode.InnerText;
                    if (dateNode != null)
                        info.ReleaseDate = dateNode.InnerText;
                    if (urlNode != null)
                        info.DownloadUrl = urlNode.InnerText;
                    if (changeLogNode != null)
                        info.ChangeLog = changeLogNode.InnerText;
                    if (sizeNode != null)
                        info.FileSize = long.TryParse(sizeNode.InnerText, out long size) ? size : 0;

                    info.IsUpdateAvailable = CompareVersions(info.Version, CurrentVersion) > 0;
                }
            }
            catch (Exception)
            {
            }

            return info;
        }

        public static void CheckForUpdateAsync(Action<UpdateInfo> callback)
        {
            ThreadPool.QueueUserWorkItem(state =>
            {
                var info = CheckForUpdate();
                callback?.Invoke(info);
            });
        }

        private static int CompareVersions(string v1, string v2)
        {
            var parts1 = v1.Split('.');
            var parts2 = v2.Split('.');

            int maxLength = Math.Max(parts1.Length, parts2.Length);

            for (int i = 0; i < maxLength; i++)
            {
                int num1 = i < parts1.Length && int.TryParse(parts1[i], out int n1) ? n1 : 0;
                int num2 = i < parts2.Length && int.TryParse(parts2[i], out int n2) ? n2 : 0;

                if (num1 > num2) return 1;
                if (num1 < num2) return -1;
            }

            return 0;
        }

        public static void DownloadUpdate(string url, string savePath, Action<int> progressCallback, Action<bool, string> completeCallback)
        {
            try
            {
                using (var client = new WebClient())
                {
                    client.DownloadProgressChanged += (s, e) =>
                    {
                        progressCallback?.Invoke(e.ProgressPercentage);
                    };

                    client.DownloadFileCompleted += (s, e) =>
                    {
                        if (e.Error != null)
                        {
                            completeCallback?.Invoke(false, e.Error.Message);
                        }
                        else if (e.Cancelled)
                        {
                            completeCallback?.Invoke(false, "下载已取消");
                        }
                        else
                        {
                            completeCallback?.Invoke(true, savePath);
                        }
                    };

                    client.DownloadFileAsync(new Uri(url), savePath);
                }
            }
            catch (Exception ex)
            {
                completeCallback?.Invoke(false, ex.Message);
            }
        }
    }

    public class UpdateForm : Form
    {
        private Label titleLabel;
        private Label versionLabel;
        private TextBox changeLogTextBox;
        private ProgressBar progressBar;
        private Button downloadButton;
        private Button laterButton;
        private UpdateInfo updateInfo;

        public UpdateForm(UpdateInfo info)
        {
            updateInfo = info;
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            this.Text = "检查更新";
            this.Size = new Size(500, 400);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            titleLabel = new Label();
            titleLabel.Text = updateInfo.IsUpdateAvailable ? "发现新版本！" : "当前已是最新版本";
            titleLabel.Font = new Font("微软雅黑", 14, FontStyle.Bold);
            titleLabel.ForeColor = updateInfo.IsUpdateAvailable ? Color.FromArgb(103, 194, 58) : Color.FromArgb(64, 158, 255);
            titleLabel.AutoSize = true;
            titleLabel.Location = new Point(20, 20);

            versionLabel = new Label();
            versionLabel.Text = string.Format("当前版本: {0}  →  最新版本: {1}", UpdateChecker.GetCurrentVersion(), updateInfo.Version);
            versionLabel.Font = new Font("微软雅黑", 10);
            versionLabel.ForeColor = Color.FromArgb(96, 98, 102);
            versionLabel.AutoSize = true;
            versionLabel.Location = new Point(20, 55);

            var changeLogLabel = new Label();
            changeLogLabel.Text = "更新内容:";
            changeLogLabel.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            changeLogLabel.ForeColor = Color.FromArgb(48, 49, 51);
            changeLogLabel.AutoSize = true;
            changeLogLabel.Location = new Point(20, 90);

            changeLogTextBox = new TextBox();
            changeLogTextBox.Multiline = true;
            changeLogTextBox.ReadOnly = true;
            changeLogTextBox.ScrollBars = ScrollBars.Vertical;
            changeLogTextBox.Location = new Point(20, 120);
            changeLogTextBox.Size = new Size(440, 160);
            changeLogTextBox.Font = new Font("微软雅黑", 9);
            changeLogTextBox.Text = updateInfo.ChangeLog ?? "暂无更新说明";
            changeLogTextBox.BackColor = Color.FromArgb(250, 250, 250);
            changeLogTextBox.BorderStyle = BorderStyle.FixedSingle;

            progressBar = new ProgressBar();
            progressBar.Location = new Point(20, 295);
            progressBar.Size = new Size(440, 25);
            progressBar.Style = ProgressBarStyle.Continuous;
            progressBar.Visible = false;

            downloadButton = new Button();
            downloadButton.Text = "立即更新";
            downloadButton.Size = new Size(100, 35);
            downloadButton.Location = new Point(280, 330);
            downloadButton.BackColor = Color.FromArgb(64, 158, 255);
            downloadButton.ForeColor = Color.White;
            downloadButton.FlatStyle = FlatStyle.Flat;
            downloadButton.Font = new Font("微软雅黑", 10);
            downloadButton.FlatAppearance.BorderSize = 0;
            downloadButton.Enabled = updateInfo.IsUpdateAvailable;
            downloadButton.Click += DownloadButton_Click;

            laterButton = new Button();
            laterButton.Text = "稍后提醒";
            laterButton.Size = new Size(100, 35);
            laterButton.Location = new Point(390, 330);
            laterButton.FlatStyle = FlatStyle.Flat;
            laterButton.Font = new Font("微软雅黑", 10);
            laterButton.Click += (s, e) => this.Close();

            this.Controls.Add(titleLabel);
            this.Controls.Add(versionLabel);
            this.Controls.Add(changeLogLabel);
            this.Controls.Add(changeLogTextBox);
            this.Controls.Add(progressBar);
            this.Controls.Add(downloadButton);
            this.Controls.Add(laterButton);
        }

        private void DownloadButton_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(updateInfo.DownloadUrl))
            {
                MessageBox.Show("下载地址无效", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            string savePath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "MedicineSystem",
                "Updates",
                string.Format("MedicineSystem_{0}.exe", updateInfo.Version)
            );

            Directory.CreateDirectory(Path.GetDirectoryName(savePath));

            progressBar.Visible = true;
            downloadButton.Enabled = false;
            downloadButton.Text = "下载中...";

            UpdateChecker.DownloadUpdate(
                updateInfo.DownloadUrl,
                savePath,
                progress => { progressBar.Value = progress; },
                (success, result) =>
                {
                    this.Invoke(new Action(() =>
                    {
                        if (success)
                        {
                            var dr = MessageBox.Show(
                                "更新下载完成，是否立即安装？",
                                "下载完成",
                                MessageBoxButtons.YesNo,
                                MessageBoxIcon.Information
                            );

                            if (dr == DialogResult.Yes)
                            {
                                try
                                {
                                    System.Diagnostics.Process.Start(result);
                                    Application.Exit();
                                }
                                catch (Exception ex)
                                {
                                    MessageBox.Show("启动更新程序失败: " + ex.Message, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                                }
                            }
                        }
                        else
                        {
                            MessageBox.Show("下载失败: " + result, "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                            downloadButton.Enabled = true;
                            downloadButton.Text = "立即更新";
                            progressBar.Visible = false;
                        }
                    }));
                }
            );
        }
    }
}
