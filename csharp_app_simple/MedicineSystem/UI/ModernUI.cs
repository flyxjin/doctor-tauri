using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace MedicineSystem.UI
{
    public static class ModernUI
    {
        public static class Colors
        {
            public static readonly Color Primary = Color.FromArgb(64, 158, 255);
            public static readonly Color PrimaryDark = Color.FromArgb(48, 128, 220);
            public static readonly Color PrimaryLight = Color.FromArgb(140, 197, 255);
            
            public static readonly Color Success = Color.FromArgb(103, 194, 58);
            public static readonly Color Warning = Color.FromArgb(230, 162, 60);
            public static readonly Color Danger = Color.FromArgb(245, 108, 108);
            public static readonly Color Info = Color.FromArgb(144, 147, 153);
            
            public static readonly Color Background = Color.FromArgb(245, 247, 250);
            public static readonly Color Surface = Color.White;
            public static readonly Color Sidebar = Color.FromArgb(30, 40, 60);
            public static readonly Color SidebarHover = Color.FromArgb(40, 55, 80);
            
            public static readonly Color TextPrimary = Color.FromArgb(48, 49, 51);
            public static readonly Color TextRegular = Color.FromArgb(96, 98, 102);
            public static readonly Color TextSecondary = Color.FromArgb(144, 147, 153);
            public static readonly Color TextWhite = Color.White;
            
            public static readonly Color Border = Color.FromArgb(228, 231, 237);
            public static readonly Color BorderLight = Color.FromArgb(242, 244, 247);
            
            public static readonly Color HoverBackground = Color.FromArgb(245, 247, 250);
            public static readonly Color SelectedBackground = Color.FromArgb(235, 245, 255);
        }

        public static class Fonts
        {
            public static readonly Font Title = new Font("微软雅黑", 16F, FontStyle.Bold);
            public static readonly Font Subtitle = new Font("微软雅黑", 14F, FontStyle.Bold);
            public static readonly Font Heading = new Font("微软雅黑", 12F, FontStyle.Bold);
            public static readonly Font Body = new Font("微软雅黑", 10F);
            public static readonly Font BodyBold = new Font("微软雅黑", 10F, FontStyle.Bold);
            public static readonly Font Small = new Font("微软雅黑", 9F);
            public static readonly Font SmallBold = new Font("微软雅黑", 9F, FontStyle.Bold);
            public static readonly Font Button = new Font("微软雅黑", 10F);
        }

        public static Button CreateButton(string text, ButtonType type = ButtonType.Primary, int width = 100, int height = 36)
        {
            var btn = new Button();
            btn.Text = text;
            btn.Width = width;
            btn.Height = height;
            btn.FlatStyle = FlatStyle.Flat;
            btn.Font = Fonts.Button;
            btn.Cursor = Cursors.Hand;
            btn.FlatAppearance.BorderSize = 0;

            switch (type)
            {
                case ButtonType.Primary:
                    btn.BackColor = Colors.Primary;
                    btn.ForeColor = Colors.TextWhite;
                    break;
                case ButtonType.Success:
                    btn.BackColor = Colors.Success;
                    btn.ForeColor = Colors.TextWhite;
                    break;
                case ButtonType.Warning:
                    btn.BackColor = Colors.Warning;
                    btn.ForeColor = Colors.TextWhite;
                    break;
                case ButtonType.Danger:
                    btn.BackColor = Colors.Danger;
                    btn.ForeColor = Colors.TextWhite;
                    break;
                case ButtonType.Info:
                    btn.BackColor = Colors.Info;
                    btn.ForeColor = Colors.TextWhite;
                    break;
                case ButtonType.Default:
                    btn.BackColor = Colors.Surface;
                    btn.ForeColor = Colors.TextRegular;
                    btn.FlatAppearance.BorderSize = 1;
                    btn.FlatAppearance.BorderColor = Colors.Border;
                    break;
            }

            btn.MouseEnter += (s, e) =>
            {
                if (type == ButtonType.Default)
                {
                    btn.BackColor = Colors.HoverBackground;
                }
                else
                {
                    btn.BackColor = ControlPaint.Light(btn.BackColor, 0.1f);
                }
            };

            btn.MouseLeave += (s, e) =>
            {
                switch (type)
                {
                    case ButtonType.Primary:
                        btn.BackColor = Colors.Primary;
                        break;
                    case ButtonType.Success:
                        btn.BackColor = Colors.Success;
                        break;
                    case ButtonType.Warning:
                        btn.BackColor = Colors.Warning;
                        break;
                    case ButtonType.Danger:
                        btn.BackColor = Colors.Danger;
                        break;
                    case ButtonType.Info:
                        btn.BackColor = Colors.Info;
                        break;
                    case ButtonType.Default:
                        btn.BackColor = Colors.Surface;
                        break;
                }
            };

            return btn;
        }

        public static TextBox CreateTextBox(string placeholder = "", int width = 200)
        {
            var txt = new TextBox();
            txt.Width = width;
            txt.Height = 32;
            txt.Font = Fonts.Body;
            txt.BorderStyle = BorderStyle.FixedSingle;
            txt.BackColor = Colors.Surface;
            txt.ForeColor = Colors.TextPrimary;
            txt.Padding = new Padding(8, 0, 8, 0);

            if (!string.IsNullOrEmpty(placeholder))
            {
                txt.Text = placeholder;
                txt.ForeColor = Colors.TextSecondary;
                txt.GotFocus += (s, e) =>
                {
                    if (txt.Text == placeholder)
                    {
                        txt.Text = "";
                        txt.ForeColor = Colors.TextPrimary;
                    }
                };
                txt.LostFocus += (s, e) =>
                {
                    if (string.IsNullOrEmpty(txt.Text))
                    {
                        txt.Text = placeholder;
                        txt.ForeColor = Colors.TextSecondary;
                    }
                };
            }

            return txt;
        }

        public static ComboBox CreateComboBox(object[] items, int width = 150)
        {
            var cmb = new ComboBox();
            cmb.Width = width;
            cmb.Height = 32;
            cmb.Font = Fonts.Body;
            cmb.FlatStyle = FlatStyle.Flat;
            cmb.BackColor = Colors.Surface;
            cmb.ForeColor = Colors.TextPrimary;
            cmb.DropDownStyle = ComboBoxStyle.DropDownList;

            if (items != null && items.Length > 0)
            {
                cmb.Items.AddRange(items);
                cmb.SelectedIndex = 0;
            }

            return cmb;
        }

        public static Panel CreateCard(int width, int height, string title = "")
        {
            var card = new Panel();
            card.Width = width;
            card.Height = height;
            card.BackColor = Colors.Surface;
            card.Padding = new Padding(0);

            return card;
        }

        public static Label CreateLabel(string text, LabelType type = LabelType.Body)
        {
            var lbl = new Label();
            lbl.Text = text;
            lbl.AutoSize = true;

            switch (type)
            {
                case LabelType.Title:
                    lbl.Font = Fonts.Title;
                    lbl.ForeColor = Colors.TextPrimary;
                    break;
                case LabelType.Subtitle:
                    lbl.Font = Fonts.Subtitle;
                    lbl.ForeColor = Colors.TextPrimary;
                    break;
                case LabelType.Heading:
                    lbl.Font = Fonts.Heading;
                    lbl.ForeColor = Colors.TextPrimary;
                    break;
                case LabelType.Body:
                    lbl.Font = Fonts.Body;
                    lbl.ForeColor = Colors.TextRegular;
                    break;
                case LabelType.Small:
                    lbl.Font = Fonts.Small;
                    lbl.ForeColor = Colors.TextSecondary;
                    break;
            }

            return lbl;
        }

        public static void StyleDataGridView(DataGridView dgv)
        {
            dgv.BackgroundColor = Colors.Surface;
            dgv.BorderStyle = BorderStyle.None;
            dgv.CellBorderStyle = DataGridViewCellBorderStyle.SingleHorizontal;
            dgv.EnableHeadersVisualStyles = false;
            dgv.GridColor = Colors.BorderLight;
            dgv.ReadOnly = true;
            dgv.AllowUserToAddRows = false;
            dgv.AllowUserToDeleteRows = false;
            dgv.AllowUserToResizeRows = false;
            dgv.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dgv.MultiSelect = false;
            dgv.RowTemplate.Height = 40;
            dgv.ColumnHeadersHeight = 42;

            dgv.DefaultCellStyle.Font = Fonts.Body;
            dgv.DefaultCellStyle.BackColor = Colors.Surface;
            dgv.DefaultCellStyle.ForeColor = Colors.TextRegular;
            dgv.DefaultCellStyle.SelectionBackColor = Colors.SelectedBackground;
            dgv.DefaultCellStyle.SelectionForeColor = Colors.TextPrimary;
            dgv.DefaultCellStyle.Padding = new Padding(10, 0, 10, 0);

            dgv.ColumnHeadersDefaultCellStyle.Font = Fonts.BodyBold;
            dgv.ColumnHeadersDefaultCellStyle.BackColor = Colors.Background;
            dgv.ColumnHeadersDefaultCellStyle.ForeColor = Colors.TextPrimary;
            dgv.ColumnHeadersDefaultCellStyle.Padding = new Padding(10, 0, 10, 0);
            dgv.ColumnHeadersBorderStyle = DataGridViewHeaderBorderStyle.None;

            dgv.RowHeadersVisible = false;
            dgv.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
        }

        public static void ShowSuccess(string message, string title = "成功")
        {
            MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        public static void ShowError(string message, string title = "错误")
        {
            MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }

        public static void ShowWarning(string message, string title = "警告")
        {
            MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Warning);
        }

        public static bool ShowConfirm(string message, string title = "确认")
        {
            return MessageBox.Show(message, title, MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes;
        }
    }

    public enum ButtonType
    {
        Primary,
        Success,
        Warning,
        Danger,
        Info,
        Default
    }

    public enum LabelType
    {
        Title,
        Subtitle,
        Heading,
        Body,
        Small
    }

    public class ModernPanel : Panel
    {
        public ModernPanel()
        {
            this.BackColor = ModernUI.Colors.Surface;
            this.Padding = new Padding(15);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            using (var pen = new Pen(ModernUI.Colors.Border, 1))
            {
                e.Graphics.DrawRectangle(pen, new Rectangle(0, 0, this.Width - 1, this.Height - 1));
            }
        }
    }

    public class CardPanel : Panel
    {
        private string _title = "";
        private bool _showShadow = true;

        public string Title
        {
            get { return _title; }
            set { _title = value; this.Invalidate(); }
        }

        public bool ShowShadow
        {
            get { return _showShadow; }
            set { _showShadow = value; this.Invalidate(); }
        }

        public CardPanel()
        {
            this.BackColor = ModernUI.Colors.Surface;
            this.Padding = new Padding(20);
            this.Margin = new Padding(10);
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            
            if (!string.IsNullOrEmpty(_title))
            {
                using (var brush = new SolidBrush(ModernUI.Colors.TextPrimary))
                {
                    e.Graphics.DrawString(_title, ModernUI.Fonts.Heading, brush, new PointF(20, 15));
                }
                
                using (var pen = new Pen(ModernUI.Colors.Border, 1))
                {
                    e.Graphics.DrawLine(pen, 20, 45, this.Width - 20, 45);
                }
            }
        }
    }
}
