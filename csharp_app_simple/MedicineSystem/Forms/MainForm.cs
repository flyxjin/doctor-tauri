using System;
using System.Drawing;
using System.Windows.Forms;
using MedicineSystem.Models;

namespace MedicineSystem.Forms
{
    public class MainForm : Form
    {
        private Panel sidebarPanel;
        private Panel contentPanel;
        private Label brandLabel;
        private Label subtitleLabel;
        private Button medicineBtn;
        private Button prescriptionBtn;
        private Button inventoryBtn;
        private Button historyBtn;
        private Button exitBtn;
        private Label versionLabel;
        private Label statsLabel;
        
        private MedicineForm medicineForm;
        private PrescriptionForm prescriptionForm;
        private InventoryForm inventoryForm;
        private HistoryForm historyForm;

        public MainForm()
        {
            InitializeComponents();
            ShowMedicineView();
            UpdateStats();
        }

        private void InitializeComponents()
        {
            this.Text = "中药材销售管理系统";
            this.Size = new Size(1200, 800);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MinimumSize = new Size(900, 600);
            this.BackColor = Color.FromArgb(240, 242, 245);

            sidebarPanel = new Panel();
            sidebarPanel.Dock = DockStyle.Left;
            sidebarPanel.Width = 200;
            sidebarPanel.BackColor = Color.FromArgb(0, 21, 41);

            brandLabel = new Label();
            brandLabel.Text = "中药材管理系统";
            brandLabel.ForeColor = Color.White;
            brandLabel.Font = new Font("微软雅黑", 14, FontStyle.Bold);
            brandLabel.AutoSize = true;
            brandLabel.Location = new Point(20, 30);

            subtitleLabel = new Label();
            subtitleLabel.Text = "专业中医药信息平台";
            subtitleLabel.ForeColor = Color.FromArgb(140, 140, 140);
            subtitleLabel.Font = new Font("微软雅黑", 9);
            subtitleLabel.AutoSize = true;
            subtitleLabel.Location = new Point(20, 60);

            medicineBtn = CreateNavButton("药材管理", 100);
            medicineBtn.Click += (s, e) => ShowMedicineView();

            prescriptionBtn = CreateNavButton("开处方", 150);
            prescriptionBtn.Click += (s, e) => ShowPrescriptionView();

            inventoryBtn = CreateNavButton("库存管理", 200);
            inventoryBtn.Click += (s, e) => ShowInventoryView();

            historyBtn = CreateNavButton("处方历史", 250);
            historyBtn.Click += (s, e) => ShowHistoryView();

            exitBtn = new Button();
            exitBtn.Text = "退出系统";
            exitBtn.Width = 160;
            exitBtn.Height = 40;
            exitBtn.Location = new Point(20, 650);
            exitBtn.FlatStyle = FlatStyle.Flat;
            exitBtn.BackColor = Color.FromArgb(255, 77, 79);
            exitBtn.ForeColor = Color.White;
            exitBtn.Font = new Font("微软雅黑", 10);
            exitBtn.Cursor = Cursors.Hand;
            exitBtn.Click += ExitBtn_Click;

            versionLabel = new Label();
            versionLabel.Text = "v1.0.0";
            versionLabel.ForeColor = Color.FromArgb(89, 89, 89);
            versionLabel.Font = new Font("微软雅黑", 8);
            versionLabel.AutoSize = true;
            versionLabel.Location = new Point(80, 700);

            sidebarPanel.Controls.Add(brandLabel);
            sidebarPanel.Controls.Add(subtitleLabel);
            sidebarPanel.Controls.Add(medicineBtn);
            sidebarPanel.Controls.Add(prescriptionBtn);
            sidebarPanel.Controls.Add(inventoryBtn);
            sidebarPanel.Controls.Add(historyBtn);
            sidebarPanel.Controls.Add(exitBtn);
            sidebarPanel.Controls.Add(versionLabel);

            contentPanel = new Panel();
            contentPanel.Dock = DockStyle.Fill;
            contentPanel.BackColor = Color.FromArgb(240, 242, 245);

            statsLabel = new Label();
            statsLabel.Text = "";
            statsLabel.ForeColor = Color.FromArgb(96, 96, 96);
            statsLabel.Font = new Font("微软雅黑", 9);
            statsLabel.AutoSize = true;
            statsLabel.Location = new Point(220, 10);

            this.Controls.Add(contentPanel);
            this.Controls.Add(sidebarPanel);
            this.Controls.Add(statsLabel);
        }

        private Button CreateNavButton(string text, int top)
        {
            var btn = new Button();
            btn.Text = text;
            btn.Width = 160;
            btn.Height = 40;
            btn.Location = new Point(20, top);
            btn.FlatStyle = FlatStyle.Flat;
            btn.BackColor = Color.Transparent;
            btn.ForeColor = Color.FromArgb(255, 255, 255, 255);
            btn.Font = new Font("微软雅黑", 10);
            btn.TextAlign = ContentAlignment.MiddleLeft;
            btn.Cursor = Cursors.Hand;
            btn.FlatAppearance.BorderSize = 0;
            return btn;
        }

        private void UpdateStats()
        {
            int count = Program.DataStore.GetMedicineCount();
            decimal value = Program.DataStore.GetTotalInventoryValue();
            int lowStock = Program.DataStore.GetLowStockCount();
            statsLabel.Text = $"药材: {count}味 | 库存总值: ¥{value:F2} | 低库存: {lowStock}种";
        }

        private void ShowMedicineView()
        {
            ClearContentPanel();
            medicineBtn.BackColor = Color.FromArgb(24, 144, 255);
            prescriptionBtn.BackColor = Color.Transparent;
            inventoryBtn.BackColor = Color.Transparent;
            historyBtn.BackColor = Color.Transparent;

            if (medicineForm == null || medicineForm.IsDisposed)
            {
                medicineForm = new MedicineForm();
                medicineForm.TopLevel = false;
                medicineForm.FormBorderStyle = FormBorderStyle.None;
                medicineForm.Dock = DockStyle.Fill;
            }
            contentPanel.Controls.Add(medicineForm);
            medicineForm.Show();
            UpdateStats();
        }

        private void ShowPrescriptionView()
        {
            ClearContentPanel();
            medicineBtn.BackColor = Color.Transparent;
            prescriptionBtn.BackColor = Color.FromArgb(24, 144, 255);
            inventoryBtn.BackColor = Color.Transparent;
            historyBtn.BackColor = Color.Transparent;

            if (prescriptionForm == null || prescriptionForm.IsDisposed)
            {
                prescriptionForm = new PrescriptionForm();
                prescriptionForm.TopLevel = false;
                prescriptionForm.FormBorderStyle = FormBorderStyle.None;
                prescriptionForm.Dock = DockStyle.Fill;
            }
            contentPanel.Controls.Add(prescriptionForm);
            prescriptionForm.Show();
        }

        private void ShowInventoryView()
        {
            ClearContentPanel();
            medicineBtn.BackColor = Color.Transparent;
            prescriptionBtn.BackColor = Color.Transparent;
            inventoryBtn.BackColor = Color.FromArgb(24, 144, 255);
            historyBtn.BackColor = Color.Transparent;

            if (inventoryForm == null || inventoryForm.IsDisposed)
            {
                inventoryForm = new InventoryForm();
                inventoryForm.TopLevel = false;
                inventoryForm.FormBorderStyle = FormBorderStyle.None;
                inventoryForm.Dock = DockStyle.Fill;
            }
            contentPanel.Controls.Add(inventoryForm);
            inventoryForm.Show();
            inventoryForm.RefreshData();
            UpdateStats();
        }

        private void ShowHistoryView()
        {
            ClearContentPanel();
            medicineBtn.BackColor = Color.Transparent;
            prescriptionBtn.BackColor = Color.Transparent;
            inventoryBtn.BackColor = Color.Transparent;
            historyBtn.BackColor = Color.FromArgb(24, 144, 255);

            if (historyForm == null || historyForm.IsDisposed)
            {
                historyForm = new HistoryForm();
                historyForm.TopLevel = false;
                historyForm.FormBorderStyle = FormBorderStyle.None;
                historyForm.Dock = DockStyle.Fill;
            }
            contentPanel.Controls.Add(historyForm);
            historyForm.Show();
            historyForm.RefreshData();
        }

        private void ClearContentPanel()
        {
            foreach (Control control in contentPanel.Controls)
            {
                control.Hide();
            }
        }

        private void ExitBtn_Click(object sender, EventArgs e)
        {
            var result = MessageBox.Show("确定要退出程序吗？", "退出确认", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (result == DialogResult.Yes)
            {
                Program.DataStore.SaveAll();
                Application.Exit();
            }
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            Program.DataStore.SaveAll();
            base.OnFormClosing(e);
        }
    }
}
