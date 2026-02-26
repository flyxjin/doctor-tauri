using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using MedicineSystem.Models;

namespace MedicineSystem.Forms
{
    public class HistoryForm : Form
    {
        private Panel headerPanel;
        private Label headerLabel;
        private Label recordCountLabel;
        private DataGridView listDataGridView;
        private DataGridView detailDataGridView;
        private List<Prescription> currentData;

        public HistoryForm()
        {
            currentData = new List<Prescription>();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            this.BackColor = Color.FromArgb(240, 242, 245);
            this.Padding = new Padding(15);

            headerPanel = new Panel();
            headerPanel.Dock = DockStyle.Top;
            headerPanel.Height = 40;
            headerPanel.BackColor = Color.White;
            headerPanel.Padding = new Padding(15, 10, 15, 10);

            headerLabel = new Label();
            headerLabel.Text = "历史处方列表";
            headerLabel.Font = new Font("微软雅黑", 12, FontStyle.Bold);
            headerLabel.ForeColor = Color.FromArgb(38, 38, 38);
            headerLabel.AutoSize = true;
            headerLabel.Location = new Point(15, 10);

            recordCountLabel = new Label();
            recordCountLabel.Text = "共 0 条记录";
            recordCountLabel.Font = new Font("微软雅黑", 9);
            recordCountLabel.ForeColor = Color.FromArgb(140, 140, 140);
            recordCountLabel.AutoSize = true;
            recordCountLabel.Location = new Point(800, 12);

            var refreshButton = new Button();
            refreshButton.Text = "刷新列表";
            refreshButton.Size = new Size(90, 28);
            refreshButton.Location = new Point(900, 8);
            refreshButton.BackColor = Color.FromArgb(24, 144, 255);
            refreshButton.ForeColor = Color.White;
            refreshButton.FlatStyle = FlatStyle.Flat;
            refreshButton.Font = new Font("微软雅黑", 9);
            refreshButton.Click += (s, e) => RefreshData();

            headerPanel.Controls.Add(headerLabel);
            headerPanel.Controls.Add(recordCountLabel);
            headerPanel.Controls.Add(refreshButton);

            var listGroup = new GroupBox();
            listGroup.Text = "处方列表";
            listGroup.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            listGroup.ForeColor = Color.FromArgb(38, 38, 38);
            listGroup.Dock = DockStyle.Top;
            listGroup.Height = 300;
            listGroup.Padding = new Padding(10);

            listDataGridView = new DataGridView();
            listDataGridView.Dock = DockStyle.Fill;
            listDataGridView.BackgroundColor = Color.White;
            listDataGridView.ReadOnly = true;
            listDataGridView.AllowUserToAddRows = false;
            listDataGridView.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            listDataGridView.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            listDataGridView.Font = new Font("微软雅黑", 9);
            listDataGridView.ColumnHeadersDefaultCellStyle.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            listDataGridView.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(250, 250, 250);
            listDataGridView.ColumnHeadersHeight = 30;
            listDataGridView.RowTemplate.Height = 28;
            listDataGridView.GridColor = Color.FromArgb(240, 240, 240);
            listDataGridView.BorderStyle = BorderStyle.None;
            listDataGridView.SelectionChanged += ListDataGridView_SelectionChanged;

            listDataGridView.Columns.Add("Id", "处方ID");
            listDataGridView.Columns.Add("PatientName", "患者姓名");
            listDataGridView.Columns.Add("PatientAge", "年龄");
            listDataGridView.Columns.Add("Diagnosis", "诊断");
            listDataGridView.Columns.Add("TotalAmount", "总金额");
            listDataGridView.Columns.Add("CreatedAt", "开具时间");

            listGroup.Controls.Add(listDataGridView);

            var detailGroup = new GroupBox();
            detailGroup.Text = "处方详情";
            detailGroup.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            detailGroup.ForeColor = Color.FromArgb(38, 38, 38);
            detailGroup.Dock = DockStyle.Fill;
            detailGroup.Padding = new Padding(10);

            detailDataGridView = new DataGridView();
            detailDataGridView.Dock = DockStyle.Fill;
            detailDataGridView.BackgroundColor = Color.White;
            detailDataGridView.ReadOnly = true;
            detailDataGridView.AllowUserToAddRows = false;
            detailDataGridView.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            detailDataGridView.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            detailDataGridView.Font = new Font("微软雅黑", 9);
            detailDataGridView.ColumnHeadersDefaultCellStyle.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            detailDataGridView.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(250, 250, 250);
            detailDataGridView.ColumnHeadersHeight = 30;
            detailDataGridView.RowTemplate.Height = 28;
            detailDataGridView.GridColor = Color.FromArgb(240, 240, 240);
            detailDataGridView.BorderStyle = BorderStyle.None;

            detailDataGridView.Columns.Add("MedicineName", "药材名称");
            detailDataGridView.Columns.Add("Quantity", "数量");
            detailDataGridView.Columns.Add("Price", "单价");
            detailDataGridView.Columns.Add("Amount", "金额");

            detailGroup.Controls.Add(detailDataGridView);

            this.Controls.Add(detailGroup);
            this.Controls.Add(listGroup);
            this.Controls.Add(headerPanel);
        }

        public void RefreshData()
        {
            currentData = Program.DataStore.Prescriptions.OrderByDescending(p => p.CreatedAt).ToList();
            listDataGridView.Rows.Clear();

            foreach (var prescription in currentData)
            {
                listDataGridView.Rows.Add(
                    prescription.Id,
                    prescription.PatientName,
                    prescription.PatientAge,
                    prescription.Diagnosis,
                    $"¥{prescription.TotalAmount:F2}",
                    prescription.CreatedAt.ToString("yyyy-MM-dd HH:mm")
                );
            }

            recordCountLabel.Text = $"共 {currentData.Count} 条记录";
            detailDataGridView.Rows.Clear();
        }

        private void ListDataGridView_SelectionChanged(object sender, EventArgs e)
        {
            if (listDataGridView.SelectedRows.Count == 0) return;

            int prescriptionId = Convert.ToInt32(listDataGridView.SelectedRows[0].Cells["Id"].Value);
            var items = Program.DataStore.GetPrescriptionItems(prescriptionId);

            detailDataGridView.Rows.Clear();
            foreach (var item in items)
            {
                detailDataGridView.Rows.Add(
                    item.MedicineName,
                    $"{item.Quantity}{item.Unit}",
                    $"¥{item.Price:F2}",
                    $"¥{item.Amount:F2}"
                );
            }
        }
    }
}
