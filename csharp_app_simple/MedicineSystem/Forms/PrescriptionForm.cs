using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using MedicineSystem.Models;

namespace MedicineSystem.Forms
{
    public class PrescriptionForm : Form
    {
        private Panel leftPanel;
        private Panel rightPanel;
        private TextBox patientNameTextBox;
        private NumericUpDown ageNumericUpDown;
        private ComboBox genderComboBox;
        private TextBox diagnosisTextBox;
        private TextBox searchTextBox;
        private DataGridView medicineDataGridView;
        private DataGridView cartDataGridView;
        private Label totalLabel;
        private List<PrescriptionItem> cart;
        private List<Medicine> searchResults;

        public PrescriptionForm()
        {
            cart = new List<PrescriptionItem>();
            searchResults = new List<Medicine>();
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            this.BackColor = Color.FromArgb(240, 242, 245);
            this.Padding = new Padding(15);

            leftPanel = new Panel();
            leftPanel.Dock = DockStyle.Left;
            leftPanel.Width = 400;
            leftPanel.BackColor = Color.White;
            leftPanel.Padding = new Padding(10);

            var patientGroup = CreateGroupBox("患者信息", 10, 200);
            var patientLayout = new TableLayoutPanel();
            patientLayout.Dock = DockStyle.Fill;
            patientLayout.ColumnCount = 2;
            patientLayout.RowCount = 4;
            patientLayout.Padding = new Padding(10);

            patientLayout.Controls.Add(CreateLabel("姓名:"), 0, 0);
            patientNameTextBox = new TextBox();
            patientNameTextBox.Font = new Font("微软雅黑", 9);
            patientNameTextBox.Width = 200;
            patientLayout.Controls.Add(patientNameTextBox, 1, 0);

            patientLayout.Controls.Add(CreateLabel("年龄:"), 0, 1);
            ageNumericUpDown = new NumericUpDown();
            ageNumericUpDown.Font = new Font("微软雅黑", 9);
            ageNumericUpDown.Width = 80;
            ageNumericUpDown.Maximum = 150;
            patientLayout.Controls.Add(ageNumericUpDown, 1, 1);

            patientLayout.Controls.Add(CreateLabel("性别:"), 0, 2);
            genderComboBox = new ComboBox();
            genderComboBox.Font = new Font("微软雅黑", 9);
            genderComboBox.Width = 80;
            genderComboBox.Items.AddRange(new object[] { "男", "女" });
            genderComboBox.SelectedIndex = 0;
            patientLayout.Controls.Add(genderComboBox, 1, 2);

            patientLayout.Controls.Add(CreateLabel("诊断:"), 0, 3);
            diagnosisTextBox = new TextBox();
            diagnosisTextBox.Font = new Font("微软雅黑", 9);
            diagnosisTextBox.Width = 200;
            patientLayout.Controls.Add(diagnosisTextBox, 1, 3);

            patientGroup.Controls.Add(patientLayout);
            leftPanel.Controls.Add(patientGroup);

            var medicineGroup = CreateGroupBox("药材库", 220, 280);
            
            var medicinePanel = new Panel();
            medicinePanel.Dock = DockStyle.Fill;
            medicinePanel.Padding = new Padding(10);

            searchTextBox = new TextBox();
            searchTextBox.Font = new Font("微软雅黑", 9);
            searchTextBox.Width = 360;
            searchTextBox.Location = new Point(10, 10);
            searchTextBox.TextChanged += SearchTextBox_TextChanged;
            medicinePanel.Controls.Add(searchTextBox);

            medicineDataGridView = new DataGridView();
            medicineDataGridView.Location = new Point(10, 40);
            medicineDataGridView.Size = new Size(360, 180);
            medicineDataGridView.BackgroundColor = Color.White;
            medicineDataGridView.ReadOnly = true;
            medicineDataGridView.AllowUserToAddRows = false;
            medicineDataGridView.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            medicineDataGridView.MultiSelect = false;
            medicineDataGridView.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            medicineDataGridView.Font = new Font("微软雅黑", 9);
            medicineDataGridView.ColumnHeadersDefaultCellStyle.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            medicineDataGridView.ColumnHeadersHeight = 30;
            medicineDataGridView.RowTemplate.Height = 25;
            medicineDataGridView.BorderStyle = BorderStyle.None;
            medicineDataGridView.GridColor = Color.FromArgb(240, 240, 240);

            medicineDataGridView.Columns.Add("Name", "名称");
            medicineDataGridView.Columns.Add("Price", "单价");
            medicineDataGridView.Columns.Add("Quantity", "库存");

            medicinePanel.Controls.Add(medicineDataGridView);

            var addButton = new Button();
            addButton.Text = "添加到处方";
            addButton.Height = 35;
            addButton.Width = 360;
            addButton.Location = new Point(10, 225);
            addButton.BackColor = Color.FromArgb(103, 194, 58);
            addButton.ForeColor = Color.White;
            addButton.FlatStyle = FlatStyle.Flat;
            addButton.Font = new Font("微软雅黑", 10);
            addButton.Click += AddButton_Click;
            medicinePanel.Controls.Add(addButton);

            medicineGroup.Controls.Add(medicinePanel);
            leftPanel.Controls.Add(medicineGroup);

            rightPanel = new Panel();
            rightPanel.Dock = DockStyle.Fill;
            rightPanel.BackColor = Color.White;
            rightPanel.Padding = new Padding(10);

            var cartGroup = CreateGroupBox("当前处方", 10, 450);
            
            var cartPanel = new Panel();
            cartPanel.Dock = DockStyle.Fill;
            cartPanel.Padding = new Padding(10);

            cartDataGridView = new DataGridView();
            cartDataGridView.Location = new Point(10, 10);
            cartDataGridView.Size = new Size(700, 350);
            cartDataGridView.BackgroundColor = Color.White;
            cartDataGridView.ReadOnly = true;
            cartDataGridView.AllowUserToAddRows = false;
            cartDataGridView.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            cartDataGridView.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            cartDataGridView.Font = new Font("微软雅黑", 9);
            cartDataGridView.ColumnHeadersDefaultCellStyle.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            cartDataGridView.ColumnHeadersHeight = 30;
            cartDataGridView.RowTemplate.Height = 30;
            cartDataGridView.BorderStyle = BorderStyle.None;
            cartDataGridView.GridColor = Color.FromArgb(240, 240, 240);

            cartDataGridView.Columns.Add("Name", "药材");
            cartDataGridView.Columns.Add("Quantity", "数量");
            cartDataGridView.Columns.Add("Price", "单价");
            cartDataGridView.Columns.Add("Amount", "小计");

            cartPanel.Controls.Add(cartDataGridView);

            totalLabel = new Label();
            totalLabel.Text = "总计: ¥ 0.00";
            totalLabel.Font = new Font("微软雅黑", 14, FontStyle.Bold);
            totalLabel.ForeColor = Color.FromArgb(231, 76, 60);
            totalLabel.Height = 40;
            totalLabel.Width = 700;
            totalLabel.Location = new Point(10, 370);
            totalLabel.TextAlign = ContentAlignment.MiddleRight;
            cartPanel.Controls.Add(totalLabel);

            cartGroup.Controls.Add(cartPanel);
            rightPanel.Controls.Add(cartGroup);

            var buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Bottom;
            buttonPanel.Height = 60;
            buttonPanel.BackColor = Color.FromArgb(250, 250, 250);
            buttonPanel.Padding = new Padding(10);

            var saveButton = CreateActionButton("保存处方", 500, Color.FromArgb(103, 194, 58));
            saveButton.Click += SaveButton_Click;

            var clearButton = CreateActionButton("清空处方", 610, Color.FromArgb(144, 147, 153));
            clearButton.Click += ClearButton_Click;

            buttonPanel.Controls.Add(saveButton);
            buttonPanel.Controls.Add(clearButton);

            rightPanel.Controls.Add(buttonPanel);

            this.Controls.Add(rightPanel);
            this.Controls.Add(leftPanel);
        }

        private GroupBox CreateGroupBox(string text, int top, int height)
        {
            var group = new GroupBox();
            group.Text = text;
            group.Font = new Font("微软雅黑", 10, FontStyle.Bold);
            group.ForeColor = Color.FromArgb(38, 38, 38);
            group.Location = new Point(10, top);
            group.Size = new Size(380, height);
            group.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            return group;
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

        private Button CreateActionButton(string text, int left, Color backColor)
        {
            var btn = new Button();
            btn.Text = text;
            btn.Size = new Size(100, 35);
            btn.Location = new Point(left, 12);
            btn.FlatStyle = FlatStyle.Flat;
            btn.BackColor = backColor;
            btn.ForeColor = Color.White;
            btn.Font = new Font("微软雅黑", 10);
            btn.Cursor = Cursors.Hand;
            btn.FlatAppearance.BorderSize = 0;
            return btn;
        }

        private void SearchTextBox_TextChanged(object sender, EventArgs e)
        {
            string keyword = searchTextBox.Text.Trim();
            if (string.IsNullOrEmpty(keyword))
            {
                searchResults.Clear();
                medicineDataGridView.Rows.Clear();
                return;
            }

            searchResults = Program.DataStore.SearchMedicines(keyword);
            medicineDataGridView.Rows.Clear();

            foreach (var medicine in searchResults)
            {
                var inventory = Program.DataStore.GetInventoryByMedicineId(medicine.Id);
                medicineDataGridView.Rows.Add(
                    medicine.Name,
                    inventory != null ? string.Format("¥{0:F2}", inventory.Price) : "¥0.00",
                    inventory != null ? string.Format("{0}g", inventory.Quantity) : "0g"
                );
            }
        }

        private void AddButton_Click(object sender, EventArgs e)
        {
            if (medicineDataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请先选择要添加的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int index = medicineDataGridView.SelectedRows[0].Index;
            if (index < 0 || index >= searchResults.Count) return;

            var medicine = searchResults[index];
            var inventory = Program.DataStore.GetInventoryByMedicineId(medicine.Id);

            if (inventory == null || inventory.Quantity <= 0)
            {
                MessageBox.Show(string.Format("药材 \"{0}\" 库存不足，无法添加", medicine.Name), "库存不足", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            using (var dialog = new QuantityInputDialog(medicine.Name, inventory.Quantity))
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    decimal qty = dialog.Quantity;
                    if (qty > inventory.Quantity)
                    {
                        MessageBox.Show(string.Format("药材 \"{0}\" 库存不足，当前库存: {1}g", medicine.Name, inventory.Quantity), "库存不足", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return;
                    }

                    var existingItem = cart.FirstOrDefault(c => c.MedicineId == medicine.Id);
                    if (existingItem != null)
                    {
                        if (existingItem.Quantity + qty > inventory.Quantity)
                        {
                            MessageBox.Show(string.Format("药材 \"{0}\" 总数量超过库存，当前库存: {1}g", medicine.Name, inventory.Quantity), "库存不足", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                            return;
                        }
                        existingItem.Quantity += qty;
                        existingItem.Amount = existingItem.Quantity * existingItem.Price;
                    }
                    else
                    {
                        cart.Add(new PrescriptionItem
                        {
                            MedicineId = medicine.Id,
                            MedicineName = medicine.Name,
                            Quantity = qty,
                            Unit = "g",
                            Price = inventory.Price,
                            Amount = qty * inventory.Price
                        });
                    }

                    RefreshCart();
                }
            }
        }

        private void RefreshCart()
        {
            cartDataGridView.Rows.Clear();
            decimal total = 0;

            foreach (var item in cart)
            {
                cartDataGridView.Rows.Add(
                    item.MedicineName,
                    string.Format("{0}{1}", item.Quantity, item.Unit),
                    string.Format("¥{0:F2}", item.Price),
                    string.Format("¥{0:F2}", item.Amount)
                );

                total += item.Amount;
            }

            totalLabel.Text = string.Format("总计: ¥ {0:F2}", total);
        }

        private void SaveButton_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(patientNameTextBox.Text))
            {
                MessageBox.Show("请填写患者姓名", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (cart.Count == 0)
            {
                MessageBox.Show("请添加药材到处方", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            try
            {
                var prescription = new Prescription
                {
                    PatientName = patientNameTextBox.Text.Trim(),
                    PatientAge = (int)ageNumericUpDown.Value,
                    PatientGender = genderComboBox.SelectedItem.ToString(),
                    Diagnosis = diagnosisTextBox.Text.Trim(),
                    TotalAmount = cart.Sum(c => c.Amount),
                    Items = cart.ToList()
                };

                int prescriptionId = Program.DataStore.AddPrescription(prescription);

                MessageBox.Show(string.Format("处方保存成功，库存已更新。\n处方编号：{0}", prescriptionId), "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                ClearForm();
            }
            catch (Exception ex)
            {
                MessageBox.Show(string.Format("保存失败：{0}", ex.Message), "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ClearButton_Click(object sender, EventArgs e)
        {
            ClearForm();
        }

        private void ClearForm()
        {
            patientNameTextBox.Clear();
            ageNumericUpDown.Value = 0;
            genderComboBox.SelectedIndex = 0;
            diagnosisTextBox.Clear();
            cart.Clear();
            RefreshCart();
        }
    }

    public class QuantityInputDialog : Form
    {
        private NumericUpDown quantityNumericUpDown;
        private decimal maxQuantity;

        public QuantityInputDialog(string medicineName, decimal maxQty)
        {
            maxQuantity = maxQty;
            InitializeComponents(medicineName);
        }

        private void InitializeComponents(string medicineName)
        {
            this.Text = string.Format("输入数量 - {0}", medicineName);
            this.Size = new Size(300, 180);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            var layout = new TableLayoutPanel();
            layout.Dock = DockStyle.Fill;
            layout.Padding = new Padding(20);
            layout.ColumnCount = 2;
            layout.RowCount = 3;

            layout.Controls.Add(CreateLabel("数量(g):"), 0, 0);
            quantityNumericUpDown = new NumericUpDown();
            quantityNumericUpDown.Font = new Font("微软雅黑", 10);
            quantityNumericUpDown.Width = 150;
            quantityNumericUpDown.Minimum = 0.1m;
            quantityNumericUpDown.Maximum = maxQuantity;
            quantityNumericUpDown.Value = 10;
            quantityNumericUpDown.DecimalPlaces = 1;
            layout.Controls.Add(quantityNumericUpDown, 1, 0);

            var infoLabel = new Label();
            infoLabel.Text = string.Format("当前库存: {0}g", maxQuantity);
            infoLabel.Font = new Font("微软雅黑", 9);
            infoLabel.ForeColor = Color.FromArgb(96, 96, 96);
            infoLabel.AutoSize = true;
            layout.Controls.Add(infoLabel, 0, 1);
            layout.SetColumnSpan(infoLabel, 2);

            var buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Bottom;
            buttonPanel.Height = 50;

            var okButton = new Button();
            okButton.Text = "确定";
            okButton.Size = new Size(80, 30);
            okButton.Location = new Point(80, 10);
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
            cancelButton.Location = new Point(170, 10);
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
            label.Font = new Font("微软雅黑", 10);
            label.AutoSize = true;
            label.Padding = new Padding(0, 10, 0, 0);
            return label;
        }

        public decimal Quantity { get { return quantityNumericUpDown.Value; } }
    }
}
