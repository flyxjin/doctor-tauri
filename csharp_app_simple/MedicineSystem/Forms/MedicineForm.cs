using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using MedicineSystem.Models;

namespace MedicineSystem.Forms
{
    public class MedicineForm : Form
    {
        private Panel searchPanel;
        private TextBox searchTextBox;
        private ComboBox categoryComboBox;
        private ComboBox natureComboBox;
        private Button searchButton;
        private Button resetButton;
        private Button addButton;
        private Button editButton;
        private Button deleteButton;
        private Button viewDetailButton;
        private DataGridView dataGridView;
        private Label statsLabel;
        private List<Medicine> currentData;

        public MedicineForm()
        {
            InitializeComponents();
            LoadData();
        }

        private void InitializeComponents()
        {
            this.BackColor = Color.FromArgb(240, 242, 245);
            this.Padding = new Padding(15);

            searchPanel = new Panel();
            searchPanel.Height = 50;
            searchPanel.Dock = DockStyle.Top;
            searchPanel.BackColor = Color.White;

            searchTextBox = new TextBox();
            searchTextBox.Location = new Point(10, 12);
            searchTextBox.Width = 200;
            searchTextBox.Font = new Font("微软雅黑", 10);

            categoryComboBox = new ComboBox();
            categoryComboBox.Location = new Point(220, 12);
            categoryComboBox.Width = 120;
            categoryComboBox.Font = new Font("微软雅黑", 9);
            categoryComboBox.Items.AddRange(new object[] { "全部分类", "补虚药", "解表药", "清热药", "泻下药", "祛风湿药", "化湿药", "利水渗湿药", "温里药", "理气药", "消食药", "驱虫药", "止血药", "活血化瘀药", "化痰止咳平喘药", "安神药", "平肝息风药", "开窍药", "收涩药" });
            categoryComboBox.SelectedIndex = 0;

            natureComboBox = new ComboBox();
            natureComboBox.Location = new Point(350, 12);
            natureComboBox.Width = 100;
            natureComboBox.Font = new Font("微软雅黑", 9);
            natureComboBox.Items.AddRange(new object[] { "全部药性", "寒", "热", "温", "凉", "平", "微寒", "微温" });
            natureComboBox.SelectedIndex = 0;

            searchButton = CreateButton("搜索", 460, Color.FromArgb(24, 144, 255));
            searchButton.Click += SearchButton_Click;

            resetButton = CreateButton("重置", 540, Color.FromArgb(144, 147, 153));
            resetButton.Click += ResetButton_Click;

            addButton = CreateButton("添加药材", 620, Color.FromArgb(103, 194, 58));
            addButton.Click += AddButton_Click;

            editButton = CreateButton("修改信息", 720, Color.FromArgb(230, 162, 60));
            editButton.Click += EditButton_Click;

            deleteButton = CreateButton("删除药材", 820, Color.FromArgb(245, 108, 108));
            deleteButton.Click += DeleteButton_Click;

            viewDetailButton = CreateButton("查看详情", 920, Color.FromArgb(64, 158, 255));
            viewDetailButton.Click += ViewDetailButton_Click;

            searchPanel.Controls.Add(searchTextBox);
            searchPanel.Controls.Add(categoryComboBox);
            searchPanel.Controls.Add(natureComboBox);
            searchPanel.Controls.Add(searchButton);
            searchPanel.Controls.Add(resetButton);
            searchPanel.Controls.Add(addButton);
            searchPanel.Controls.Add(editButton);
            searchPanel.Controls.Add(deleteButton);
            searchPanel.Controls.Add(viewDetailButton);

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
            dataGridView.CellDoubleClick += DataGridView_CellDoubleClick;

            statsLabel = new Label();
            statsLabel.Dock = DockStyle.Bottom;
            statsLabel.Height = 30;
            statsLabel.BackColor = Color.White;
            statsLabel.ForeColor = Color.FromArgb(96, 96, 96);
            statsLabel.Font = new Font("微软雅黑", 9);
            statsLabel.Padding = new Padding(10, 5, 0, 0);

            this.Controls.Add(dataGridView);
            this.Controls.Add(searchPanel);
            this.Controls.Add(statsLabel);
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

        public void LoadData()
        {
            string keyword = searchTextBox.Text.Trim();
            string category = categoryComboBox.SelectedItem?.ToString();
            string nature = natureComboBox.SelectedItem?.ToString();

            currentData = Program.DataStore.SearchMedicines(keyword, category, nature);

            dataGridView.Columns.Clear();
            dataGridView.Columns.Add("Id", "ID");
            dataGridView.Columns.Add("Name", "名称");
            dataGridView.Columns.Add("Alias", "别名");
            dataGridView.Columns.Add("Category", "分类");
            dataGridView.Columns.Add("Nature", "药性");
            dataGridView.Columns.Add("Taste", "药味");
            dataGridView.Columns.Add("Meridian", "归经");

            dataGridView.Columns["Id"].Visible = false;

            foreach (var medicine in currentData)
            {
                dataGridView.Rows.Add(
                    medicine.Id,
                    medicine.Name,
                    medicine.Alias,
                    medicine.Category,
                    medicine.Nature,
                    medicine.Taste,
                    medicine.Meridian
                );
            }

            statsLabel.Text = $"共 {currentData.Count} 味药材";
        }

        private void SearchButton_Click(object sender, EventArgs e)
        {
            LoadData();
        }

        private void ResetButton_Click(object sender, EventArgs e)
        {
            searchTextBox.Clear();
            categoryComboBox.SelectedIndex = 0;
            natureComboBox.SelectedIndex = 0;
            LoadData();
        }

        private void AddButton_Click(object sender, EventArgs e)
        {
            using (var dialog = new MedicineEditForm())
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    var medicine = dialog.GetMedicine();
                    int medId = Program.DataStore.AddMedicine(medicine);

                    var inventory = new Inventory
                    {
                        MedicineId = medId,
                        MedicineName = medicine.Name,
                        Quantity = 0,
                        Unit = "g",
                        Price = 0,
                        MinStock = 10
                    };
                    Program.DataStore.AddInventory(inventory);

                    MessageBox.Show("药材添加成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    LoadData();
                }
            }
        }

        private void EditButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请先选择要编辑的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int id = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["Id"].Value);
            var medicine = currentData.FirstOrDefault(m => m.Id == id);

            if (medicine != null)
            {
                using (var dialog = new MedicineEditForm(medicine))
                {
                    if (dialog.ShowDialog() == DialogResult.OK)
                    {
                        var updated = dialog.GetMedicine();
                        updated.Id = id;
                        Program.DataStore.UpdateMedicine(updated);
                        MessageBox.Show("修改成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        LoadData();
                    }
                }
            }
        }

        private void DeleteButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请先选择要删除的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int id = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["Id"].Value);
            string name = dataGridView.SelectedRows[0].Cells["Name"].Value.ToString();

            var result = MessageBox.Show($"确定要删除药材 \"{name}\" 吗？\n此操作将同时删除库存记录！", "确认删除", MessageBoxButtons.YesNo, MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                Program.DataStore.DeleteMedicine(id);
                MessageBox.Show("删除成功！", "成功", MessageBoxButtons.OK, MessageBoxIcon.Information);
                LoadData();
            }
        }

        private void ViewDetailButton_Click(object sender, EventArgs e)
        {
            if (dataGridView.SelectedRows.Count == 0)
            {
                MessageBox.Show("请先选择要查看的药材", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            int id = Convert.ToInt32(dataGridView.SelectedRows[0].Cells["Id"].Value);
            var medicine = currentData.FirstOrDefault(m => m.Id == id);

            if (medicine != null)
            {
                using (var dialog = new MedicineDetailForm(medicine))
                {
                    dialog.ShowDialog();
                }
            }
        }

        private void DataGridView_CellDoubleClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex >= 0)
            {
                viewDetailButton.PerformClick();
            }
        }
    }

    public class MedicineEditForm : Form
    {
        private TextBox nameTextBox;
        private TextBox aliasTextBox;
        private ComboBox categoryComboBox;
        private ComboBox natureComboBox;
        private TextBox tasteTextBox;
        private TextBox meridianTextBox;
        private TextBox efficacyTextBox;
        private TextBox indicationsTextBox;
        private TextBox usageTextBox;
        private TextBox dosageTextBox;
        private TextBox contraindicationTextBox;
        private TextBox notesTextBox;
        private Medicine medicine;

        public MedicineEditForm(Medicine med = null)
        {
            medicine = med ?? new Medicine();
            InitializeComponents();
            PopulateFields();
        }

        private void InitializeComponents()
        {
            this.Text = medicine.Id > 0 ? "编辑药材" : "添加药材";
            this.Size = new Size(500, 550);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            var layout = new TableLayoutPanel();
            layout.Dock = DockStyle.Fill;
            layout.Padding = new Padding(20);
            layout.ColumnCount = 2;
            layout.RowCount = 13;

            layout.Controls.Add(CreateLabel("药材名称*:"), 0, 0);
            nameTextBox = CreateTextBox();
            layout.Controls.Add(nameTextBox, 1, 0);

            layout.Controls.Add(CreateLabel("别名:"), 0, 1);
            aliasTextBox = CreateTextBox();
            layout.Controls.Add(aliasTextBox, 1, 1);

            layout.Controls.Add(CreateLabel("分类:"), 0, 2);
            categoryComboBox = CreateComboBox(new[] { "", "补虚药", "解表药", "清热药", "泻下药", "祛风湿药", "化湿药", "利水渗湿药", "温里药", "理气药", "消食药", "驱虫药", "止血药", "活血化瘀药", "化痰止咳平喘药", "安神药", "平肝息风药", "开窍药", "收涩药" });
            layout.Controls.Add(categoryComboBox, 1, 2);

            layout.Controls.Add(CreateLabel("药性:"), 0, 3);
            natureComboBox = CreateComboBox(new[] { "", "寒", "热", "温", "凉", "平", "微寒", "微温", "大寒" });
            layout.Controls.Add(natureComboBox, 1, 3);

            layout.Controls.Add(CreateLabel("药味:"), 0, 4);
            tasteTextBox = CreateTextBox();
            layout.Controls.Add(tasteTextBox, 1, 4);

            layout.Controls.Add(CreateLabel("归经:"), 0, 5);
            meridianTextBox = CreateTextBox();
            layout.Controls.Add(meridianTextBox, 1, 5);

            layout.Controls.Add(CreateLabel("功效:"), 0, 6);
            efficacyTextBox = CreateTextBox();
            efficacyTextBox.Height = 50;
            layout.Controls.Add(efficacyTextBox, 1, 6);

            layout.Controls.Add(CreateLabel("主治:"), 0, 7);
            indicationsTextBox = CreateTextBox();
            indicationsTextBox.Height = 50;
            layout.Controls.Add(indicationsTextBox, 1, 7);

            layout.Controls.Add(CreateLabel("用法:"), 0, 8);
            usageTextBox = CreateTextBox();
            layout.Controls.Add(usageTextBox, 1, 8);

            layout.Controls.Add(CreateLabel("用量:"), 0, 9);
            dosageTextBox = CreateTextBox();
            layout.Controls.Add(dosageTextBox, 1, 9);

            layout.Controls.Add(CreateLabel("禁忌:"), 0, 10);
            contraindicationTextBox = CreateTextBox();
            contraindicationTextBox.Height = 50;
            layout.Controls.Add(contraindicationTextBox, 1, 10);

            layout.Controls.Add(CreateLabel("备注:"), 0, 11);
            notesTextBox = CreateTextBox();
            layout.Controls.Add(notesTextBox, 1, 11);

            var buttonPanel = new Panel();
            buttonPanel.Dock = DockStyle.Bottom;
            buttonPanel.Height = 50;
            buttonPanel.BackColor = Color.FromArgb(250, 250, 250);

            var saveButton = new Button();
            saveButton.Text = "保存";
            saveButton.Size = new Size(80, 30);
            saveButton.Location = new Point(280, 10);
            saveButton.BackColor = Color.FromArgb(24, 144, 255);
            saveButton.ForeColor = Color.White;
            saveButton.FlatStyle = FlatStyle.Flat;
            saveButton.Click += (s, e) =>
            {
                if (string.IsNullOrWhiteSpace(nameTextBox.Text))
                {
                    MessageBox.Show("请输入药材名称！", "提示", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }
                this.DialogResult = DialogResult.OK;
                this.Close();
            };

            var cancelButton = new Button();
            cancelButton.Text = "取消";
            cancelButton.Size = new Size(80, 30);
            cancelButton.Location = new Point(370, 10);
            cancelButton.FlatStyle = FlatStyle.Flat;
            cancelButton.Click += (s, e) =>
            {
                this.DialogResult = DialogResult.Cancel;
                this.Close();
            };

            buttonPanel.Controls.Add(saveButton);
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

        private TextBox CreateTextBox()
        {
            var textBox = new TextBox();
            textBox.Font = new Font("微软雅黑", 9);
            textBox.Width = 300;
            textBox.Anchor = AnchorStyles.Left | AnchorStyles.Right;
            return textBox;
        }

        private ComboBox CreateComboBox(string[] items)
        {
            var comboBox = new ComboBox();
            comboBox.Font = new Font("微软雅黑", 9);
            comboBox.Width = 300;
            comboBox.Items.AddRange(items);
            comboBox.Anchor = AnchorStyles.Left | AnchorStyles.Right;
            return comboBox;
        }

        private void PopulateFields()
        {
            nameTextBox.Text = medicine.Name;
            aliasTextBox.Text = medicine.Alias;
            categoryComboBox.SelectedItem = medicine.Category;
            natureComboBox.SelectedItem = medicine.Nature;
            tasteTextBox.Text = medicine.Taste;
            meridianTextBox.Text = medicine.Meridian;
            efficacyTextBox.Text = medicine.Efficacy;
            indicationsTextBox.Text = medicine.Indications;
            usageTextBox.Text = medicine.Usage;
            dosageTextBox.Text = medicine.Dosage;
            contraindicationTextBox.Text = medicine.Contraindication;
            notesTextBox.Text = medicine.Notes;
        }

        public Medicine GetMedicine()
        {
            medicine.Name = nameTextBox.Text.Trim();
            medicine.Alias = aliasTextBox.Text.Trim();
            medicine.Category = categoryComboBox.SelectedItem?.ToString() ?? "";
            medicine.Nature = natureComboBox.SelectedItem?.ToString() ?? "";
            medicine.Taste = tasteTextBox.Text.Trim();
            medicine.Meridian = meridianTextBox.Text.Trim();
            medicine.Efficacy = efficacyTextBox.Text.Trim();
            medicine.Indications = indicationsTextBox.Text.Trim();
            medicine.Usage = usageTextBox.Text.Trim();
            medicine.Dosage = dosageTextBox.Text.Trim();
            medicine.Contraindication = contraindicationTextBox.Text.Trim();
            medicine.Notes = notesTextBox.Text.Trim();
            return medicine;
        }
    }

    public class MedicineDetailForm : Form
    {
        public MedicineDetailForm(Medicine medicine)
        {
            this.Text = "药材详情";
            this.Size = new Size(500, 600);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.BackColor = Color.White;

            var panel = new Panel();
            panel.Dock = DockStyle.Fill;
            panel.Padding = new Padding(20);
            panel.AutoScroll = true;

            var titleLabel = new Label();
            titleLabel.Text = medicine.Name;
            titleLabel.Font = new Font("微软雅黑", 16, FontStyle.Bold);
            titleLabel.ForeColor = Color.FromArgb(64, 158, 255);
            titleLabel.AutoSize = true;
            titleLabel.Location = new Point(20, 20);
            panel.Controls.Add(titleLabel);

            int y = 60;
            AddDetailRow(panel, "别名", medicine.Alias, ref y);
            AddDetailRow(panel, "分类", medicine.Category, ref y);
            AddDetailRow(panel, "药性", medicine.Nature, ref y);
            AddDetailRow(panel, "药味", medicine.Taste, ref y);
            AddDetailRow(panel, "归经", medicine.Meridian, ref y);
            AddDetailRow(panel, "功效", medicine.Efficacy, ref y, true);
            AddDetailRow(panel, "主治", medicine.Indications, ref y, true);
            AddDetailRow(panel, "用法", medicine.Usage, ref y);
            AddDetailRow(panel, "用量", medicine.Dosage, ref y);
            AddDetailRow(panel, "禁忌", medicine.Contraindication, ref y, true);
            AddDetailRow(panel, "备注", medicine.Notes, ref y);

            var closeButton = new Button();
            closeButton.Text = "关闭";
            closeButton.Size = new Size(80, 30);
            closeButton.Location = new Point(200, y + 20);
            closeButton.FlatStyle = FlatStyle.Flat;
            closeButton.Click += (s, e) => this.Close();
            panel.Controls.Add(closeButton);

            this.Controls.Add(panel);
        }

        private void AddDetailRow(Panel panel, string label, string value, ref int y, bool multiline = false)
        {
            var labelControl = new Label();
            labelControl.Text = label + ":";
            labelControl.Font = new Font("微软雅黑", 9, FontStyle.Bold);
            labelControl.ForeColor = Color.FromArgb(96, 96, 96);
            labelControl.Location = new Point(20, y);
            labelControl.AutoSize = true;
            panel.Controls.Add(labelControl);

            var valueControl = new Label();
            valueControl.Text = string.IsNullOrEmpty(value) ? "暂无" : value;
            valueControl.Font = new Font("微软雅黑", 9);
            valueControl.ForeColor = Color.FromArgb(38, 38, 38);
            valueControl.Location = new Point(80, y);
            valueControl.Width = 380;
            valueControl.Height = multiline ? 60 : 25;
            valueControl.AutoSize = false;
            panel.Controls.Add(valueControl);

            y += multiline ? 70 : 35;
        }
    }
}
