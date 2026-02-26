using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using MedicineSystem.Models;

namespace MedicineSystem.Forms
{
    public class InventoryForm : Form
    {
        private Panel statsPanel;
        private Label totalMedsLabel;
        private Label totalValueLabel;
        private Label lowStockLabel;
        private Panel warningPanel;
        private Label warningLabel;
        private Panel searchPanel;
        private TextBox searchTextBox;
        private ComboBox stockFilterComboBox;
        private Button searchButton;
        private Button refreshButton;
        private DataGridView dataGridView;
        private List<Inventory> currentData;

        public InventoryForm()
        {
            currentData = new List<Inventory>();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            this.BackColor = Color.FromArgb(240, 242, 245);
            this.Padding = new Padding(15);

            statsPanel = new Panel();
            statsPanel.Dock = DockStyle.Top;
            statsPanel.Height = 50;
            statsPanel.BackColor = Color.White;
            statsPanel.Padding = new Padding(15, 10, 15, 10);

            totalMedsLabel = new Label();
            totalMedsLabel.Text = "药材种类: 0";
            totalMedsLabel.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            totalMedsLabel.ForeColor = Color.FromArgb(64, 158, 255);
            totalMedsLabel.AutoSize = true;
            totalMedsLabel.Location = new Point(15, 15);

            totalValueLabel = new Label();
            totalValueLabel.Text = "库存总值: ¥0.00";
            totalValueLabel.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            totalValueLabel.ForeColor = Color.FromArgb(103, 194, 58);
            totalValueLabel.AutoSize = true;
            totalValueLabel.Location = new Point(150, 15);

            lowStockLabel = new Label();
            lowStockLabel.Text = "低库存: 0";
            lowStockLabel.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            lowStockLabel.ForeColor = Color.FromArgb(245, 108, 108);
            lowStockLabel.AutoSize = true;
            lowStockLabel.Location = new Point(320, 15);

            statsPanel.Controls.Add(totalMedsLabel);
            statsPanel.Controls.Add(totalValueLabel);
            statsPanel.Controls.Add(lowStockLabel);

            warningPanel = new Panel();
            warningPanel.Dock = DockStyle.Top;
            warningPanel.Height = 40;
            warningPanel.BackColor = Color.FromArgb(255, 250, 240);
            warningPanel.Padding = new Padding(15, 10, 15, 10);

            warningLabel = new Label();
            warningLabel.Text = "库存状态正常";
            warningLabel.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            warningLabel.ForeColor = Color.FromArgb(103, 194, 58);
            warningLabel.AutoSize = true;
            warningLabel.Location = new Point(15, 12);

            warningPanel.Controls.Add(warningLabel);

            searchPanel = new Panel();
            searchPanel.Dock = DockStyle.Top;
            searchPanel.Height = 50;
            searchPanel.BackColor = Color.White;
            searchPanel.Padding = new Padding(10);

            searchTextBox = new TextBox();
            searchTextBox.Location = new Point(10, 12);
            searchTextBox.Width = 200;
            searchTextBox.Font = new Font("微软雅黑", 9);

            stockFilterComboBox = new ComboBox();
            stockFilterComboBox.Location = new Point(220, 12);
            stockFilterComboBox.Width = 100;
            stockFilterComboBox.Font = new Font("微软雅黑", 9);
            stockFilterComboBox.Items.AddRange(new object[] { "全部", "库存充足", "低库存", "缺货" });
            stockFilterComboBox.SelectedIndex = 0;

            searchButton = CreateButton("搜索", 330, Color.FromArgb(24, 144, 255));
            searchButton.Click += (s, e) => RefreshData();

            refreshButton = CreateButton("刷新", 420, Color.FromArgb(144, 147, 153));
            refreshButton.Click += (s, e) => RefreshData();

            var stockInButton = CreateButton("药材入库", 510, Color.FromArgb(103, 194, 58));
            stockInButton.Click += StockInButton_Click;

            var stockOutButton = CreateButton("药材出库", 610, Color.FromArgb(230, 162, 60));
            stockOutButton.Click += StockOutButton_Click;

            var adjustButton = CreateButton("库存调整", 710, Color.FromArgb(64, 158, 255));
            adjustButton.Click += AdjustButton_Click;

            searchPanel.Controls.Add(searchTextBox);
            searchPanel.Controls.Add(stockFilterComboBox);
            searchPanel.Controls.Add(searchButton);
            searchPanel.Controls.Add(refreshButton);
            searchPanel.Controls.Add(stockInButton);
            searchPanel.Controls.Add(stockOutButton);
            searchPanel.Controls.Add(adjustButton);

            dataGridView = new DataGridView();
            dataGridView.Dock = DockStyle.Fill;
            dataGridView.BackgroundColor = Color.White;
            dataGridView.ReadOnly = true;
            dataGridView.AllowUserToAddRows = false;
            dataGridView.AllowUserToDeleteRows = false;
            dataGridView.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dataGridView.MultiSelect = false;
            dataGridView.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            dataGridView.Font = new Font("微软雅黑", 9);
            dataGridView.ColumnHeadersDefaultCellStyle.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            dataGridView.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(250, 250, 250);
            dataGridView.ColumnHeadersHeight = 35;
            dataGridView.RowTemplate.Height = 30;
            dataGridView.GridColor = Color.FromArgb(240, 240, 240);
            dataGridView.BorderStyle = BorderStyle.None;

            dataGridView.Columns.Add("MedicineId", "ID");
            dataGridView.Columns.Add("MedicineName", "药材名称");
            dataGridView.Columns.Add("Category", "分类");
            dataGridView.Columns.Add("Quantity", "库存数量");
            dataGridView.Columns.Add("Unit", "单位");
            dataGridView.Columns.Add("Price", "单价");
            dataGridView.Columns.Add("StockValue", "库存总值");
            dataGridView.Columns.Add("MinStock", "最低库存");
            dataGridView.Columns.Add("Notes", "备注");

            dataGridView.Columns["MedicineId"].Visible = false;

            this.Controls.Add(dataGridView);
            this.Controls.Add(searchPanel);
            this.Controls.Add(warningPanel);
            this.Controls.Add(statsPanel);
        }

        private Button CreateButton(string text, int left, Color backColor)
        {
            var btn = new Button();
            btn.Text = text;
            btn.Location = new Point(left, 8);
            btn.Size = new Size(90, 30);
            btn.FlatStyle = FlatStyle.Flat;
            btn.BackColor = backColor;
            btn.ForeColor = Color.White;
            btn.Font = new Font("微软雅黑", 9);
            btn.Cursor = Cursors.Hand;
            btn.FlatAppearance.BorderSize = 0;
            return btn;
        }

        public void RefreshData()
        {
            string keyword = searchTextBox.Text.Trim();
            string filter = stockFilterComboBox.SelectedItem?.ToString();

            currentData.Clear();
            dataGridView.Rows.Clear();

            foreach (var inventory in Program.DataStore.Inventory)
            {
                var medicine = Program.DataStore.GetMedicineById(inventory.MedicineId);
                if (medicine == null) continue;

                if (!string.IsNullOrEmpty(keyword) && !medicine.Name.Contains(keyword))
                    continue;

                bool isLowStock = inventory.Quantity <= inventory.MinStock;
                bool isOutOfStock = inventory.Quantity == 0;

                if (filter == "库存充足" && isLowStock) continue;
                if (filter == "低库存" && (!isLowStock || isOutOfStock)) continue;
                if (filter == "缺货" && !isOutOfStock) continue;

                currentData.Add(inventory);

                int rowIndex = dataGridView.Rows.Add(
                    inventory.MedicineId,
                    inventory.MedicineName,
                    medicine.Category,
                    inventory.Quantity,
                    inventory.Unit,
                    $"¥{inventory.Price:F2}",
                    $"¥{inventory.Quantity * inventory.Price:F2}",
                    inventory.MinStock,
                    inventory.Notes
                );

                if (inventory.Quantity == 0)
                {
                    dataGridView.Rows[rowIndex].Cells["Quantity"].Style.BackColor = Color.FromArgb(255, 150, 150);
                }
                else if (inventory.Quantity <= inventory.MinStock)
                {
                    dataGridView.Rows[rowIndex].Cells["Quantity"].Style.BackColor = Color.FromArgb(255, 220, 150);
                }
            }

            UpdateStats();
        }

        private void UpdateStats()
        {
            int totalMeds = Program.DataStore.Inventory.Count;
            decimal totalValue = Program.DataStore.GetTotalInventoryValue();
            var lowStockItems = Program.DataStore.GetLowStockItems();

            totalMedsLabel.Text = $"药材种类: {totalMeds}";
            totalValueLabel.Text = $"库存总值: ¥{totalValue:F2}";
            lowStockLabel.Text = $"低库存: {lowStockItems.Count}";

            if (lowStockItems.Count > 0)
            {
                var names = lowStockItems.Take(5).Select(i => i.MedicineName);
                warningLabel.Text = $"库存预警：{string.Join(", ", names)}{(lowStockItems.Count > 5 ? "..." : "")} 库存不足！";
                warningLabel.ForeColor = Color.FromArgb(255, 77, 79);
            }
            else
            {
                warningLabel.Text = "库存状态正常";
                warningLabel.ForeColor = Color.FromArgb(103, 194, 58);
            }
        }

        private void StockInButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请选择要入库的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int medicineId = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["MedicineId"].Value);
            string medicineName = dataGridView.SelectedRows[0].Cells["MedicineName"].Value.ToString();
            var inventory = currentData.FirstOrDefault(i => i.MedicineId == medicineId);

            using (var dialog = new StockDialog(medicineName, "入库", inventory))
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    Program.DataStore.StockIn(medicineId, dialog.Quantity, dialog.Price, dialog.Notes);
                    MessageBox.Show("入库成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    RefreshData();
                }
            }
        }

        private void StockOutButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请选择要出库的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int medicineId = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["MedicineId"].Value);
            string medicineName = dataGridView.SelectedRows[0].Cells["MedicineName"].Value.ToString();
            var inventory = currentData.FirstOrDefault(i => i.MedicineId == medicineId);

            using (var dialog = new StockDialog(medicineName, "出库", inventory))
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    if (dialog.Quantity > inventory.Quantity)
                    {
                        MessageBox.Show("出库数量不能大于当前库存！", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }
                    Program.DataStore.StockOut(medicineId, dialog.Quantity, dialog.Notes);
                    MessageBox.Show("出库成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    RefreshData();
                }
            }
        }

        private void AdjustButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请选择要调整的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int medicineId = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["MedicineId"].Value);
            string medicineName = dataGridView.SelectedRows[0].Cells["MedicineName"].Value.ToString();
            var inventory = currentData.FirstOrDefault(i => i.MedicineId == medicineId);

            using (var dialog = new StockAdjustDialog(medicineName, inventory))
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    inventory.Quantity = dialog.Quantity;
                    inventory.Price = dialog.Price;
                    inventory.MinStock = dialog.MinStock;
                    inventory.Notes = dialog.Notes;
                    Program.DataStore.UpdateInventory(inventory);
                    MessageBox.Show("库存调整成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    RefreshData();
                }
            }
        }
    }

    public class StockDialog : Form
    {
        private NumericUpDown quantityNumericUpDown;
        private NumericUpDown priceNumericUpDown;
        private TextBox notesTextBox;
        private string operation;

        public StockDialog(string medicineName, string operation, Inventory inventory)
        {
            this.operation = operation;
            this.Text = $"{operation}操作 - {medicineName}";
            this.Size = new Size(350, 250);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            var layout = new TableLayoutPanel();
            layout.Dock = DockStyle.Fill;
            layout.Padding = new Padding(20);
            layout.ColumnCount = 2;
            layout.RowCount = 4;

            layout.Controls.Add(CreateLabel("数量:"), 0, 0);
            quantityNumericUpDown = new NumericUpDown();
            quantityNumericUpDown.Font = new Font("微软雅黑", 9);
            quantityNumericUpDown.Width = 180;
            quantityNumericUpDown.Minimum = 0.01m;
            quantityNumericUpDown.Maximum = 10000;
            quantityNumericUpDown.DecimalPlaces = 2;
            quantityNumericUpDown.Value = 1;
            layout.Controls.Add(quantityNumericUpDown, 1, 0);

            if (operation == "入库")
            {
                layout.Controls.Add(CreateLabel("进价:"), 0, 1);
                priceNumericUpDown = new NumericUpDown();
                priceNumericUpDown.Font = new Font("微软雅黑", 9);
                priceNumericUpDown.Width = 180;
                priceNumericUpDown.Minimum = 0;
                priceNumericUpDown.Maximum = 10000;
                priceNumericUpDown.DecimalPlaces = 2;
                priceNumericUpDown.Value = inventory?.Price ?? 0;
                layout.Controls.Add(priceNumericUpDown, 1, 1);
            }

            layout.Controls.Add(CreateLabel("备注:"), 0, 2);
            notesTextBox = new TextBox();
            notesTextBox.Font = new Font("微软雅黑", 9);
            notesTextBox.Width = 180;
            layout.Controls.Add(notesTextBox, 1, 2);

            if (operation == "出库")
            {
                var infoLabel = new Label();
                infoLabel.Text = $"当前库存: {inventory?.Quantity ?? 0} g";
                infoLabel.Font = new Font("微软雅黑", 9);
                infoLabel.ForeColor = Color.FromArgb(96, 96, 96);
                infoLabel.AutoSize = true;
                layout.Controls.Add(infoLabel, 0, 3);
                layout.SetColumnSpan(infoLabel, 2);
            }

            var buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Bottom;
            buttonPanel.Height = 50;

            var okButton = new Button();
            okButton.Text = "确认";
            okButton.Size = new Size(80, 30);
            okButton.Location = new Point(100, 10);
            okButton.BackColor = Color.FromArgb(24, 144, 255);
            okButton.ForeColor = Color.White;
            okButton.FlatStyle = FlatStyle.Flat;
            okButton.Click += (s, e) =>
            {
                this.DialogResult = DialogResult.OK;
                this.Close();
            };

            var cancelButton = new Button();
            cancelButton.Text = "取消";
            cancelButton.Size = new Size(80, 30);
            cancelButton.Location = new Point(190, 10);
            cancelButton.FlatStyle = FlatStyle.Flat;
            cancelButton.Click += (s, e) =>
            {
                this.DialogResult = DialogResult.Cancel;
                this.Close();
            };

            buttonPanel.Controls.Add(okButton);
            buttonPanel.Controls.Add(cancelButton);

            this.Controls.Add(layout);
            this.Controls.Add(buttonPanel);
        }

        private Label CreateLabel(string text)
        {
            var label = new Label();
            label.Text = text;
            label.Font = new Font("微软雅黑", 9);
            label.AutoSize = true;
            label.Padding = new Padding(0, 8, 0, 0);
            return label;
        }

        public decimal Quantity => quantityNumericUpDown.Value;
        public decimal Price => priceNumericUpDown?.Value ?? 0;
        public string Notes => notesTextBox.Text;
    }

    public class StockAdjustDialog : Form
    {
        private NumericUpDown quantityNumericUpDown;
        private NumericUpDown priceNumericUpDown;
        private NumericUpDown minStockNumericUpDown;
        private TextBox notesTextBox;

        public StockAdjustDialog(string medicineName, Inventory inventory)
        {
            this.Text = $"库存调整 - {medicineName}";
            this.Size = new Size(350, 280);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            var layout = new TableLayoutPanel();
            layout.Dock = DockStyle.Fill;
            layout.Padding = new Padding(20);
            layout.ColumnCount = 2;
            layout.RowCount = 5;

            layout.Controls.Add(CreateLabel("调整后库存:"), 0, 0);
            quantityNumericUpDown = new NumericUpDown();
            quantityNumericUpDown.Font = new Font("微软雅黑", 9);
            quantityNumericUpDown.Width = 180;
            quantityNumericUpDown.Minimum = 0;
            quantityNumericUpDown.Maximum = 10000;
            quantityNumericUpDown.DecimalPlaces = 2;
            quantityNumericUpDown.Value = inventory?.Quantity ?? 0;
            layout.Controls.Add(quantityNumericUpDown, 1, 0);

            layout.Controls.Add(CreateLabel("单价:"), 0, 1);
            priceNumericUpDown = new NumericUpDown();
            priceNumericUpDown.Font = new Font("微软雅黑", 9);
            priceNumericUpDown.Width = 180;
            priceNumericUpDown.Minimum = 0;
            priceNumericUpDown.Maximum = 10000;
            priceNumericUpDown.DecimalPlaces = 2;
            priceNumericUpDown.Value = inventory?.Price ?? 0;
            layout.Controls.Add(priceNumericUpDown, 1, 1);

            layout.Controls.Add(CreateLabel("最低库存:"), 0, 2);
            minStockNumericUpDown = new NumericUpDown();
            minStockNumericUpDown.Font = new Font("微软雅黑", 9);
            minStockNumericUpDown.Width = 180;
            minStockNumericUpDown.Minimum = 0;
            minStockNumericUpDown.Maximum = 10000;
            minStockNumericUpDown.DecimalPlaces = 2;
            minStockNumericUpDown.Value = inventory?.MinStock ?? 10;
            layout.Controls.Add(minStockNumericUpDown, 1, 2);

            layout.Controls.Add(CreateLabel("备注:"), 0, 3);
            notesTextBox = new TextBox();
            notesTextBox.Font = new Font("微软雅黑", 9);
            notesTextBox.Width = 180;
            notesTextBox.Text = inventory?.Notes ?? "";
            layout.Controls.Add(notesTextBox, 1, 3);

            var buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Bottom;
            buttonPanel.Height = 50;

            var okButton = new Button();
            okButton.Text = "确认";
            okButton.Size = new Size(80, 30);
            okButton.Location = new Point(100, 10);
            okButton.BackColor = Color.FromArgb(24, 144, 255);
            okButton.ForeColor = Color.White;
            okButton.FlatStyle = FlatStyle.Flat;
            okButton.Click += (s, e) =>
            {
                this.DialogResult = DialogResult.OK;
                this.Close();
            };

            var cancelButton = new Button();
            cancelButton.Text = "取消";
            cancelButton.Size = new Size(80, 30);
            cancelButton.Location = new Point(190, 10);
            cancelButton.FlatStyle = FlatStyle.Flat;
            cancelButton.Click += (s, e) =>
            {
                this.DialogResult = DialogResult.Cancel;
                this.Close();
            };

            buttonPanel.Controls.Add(okButton);
            buttonPanel.Controls.Add(cancelButton);

            this.Controls.Add(layout);
            this.Controls.Add(buttonPanel);
        }

        private Label CreateLabel(string text)
        {
            var label = new Label();
            label.Text = text;
            label.Font = new Font("微软雅黑", 9);
            label.AutoSize = true;
            label.Padding = new Padding(0, 8, 0, 0);
            return label;
        }

        public decimal Quantity => quantityNumericUpDown.Value;
        public decimal Price => priceNumericUpDown.Value;
        public decimal MinStock => minStockNumericUpDown.Value;
        public string Notes => notesTextBox.Text;
    }
}
