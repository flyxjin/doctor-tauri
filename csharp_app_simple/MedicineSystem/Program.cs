using System;
using System.Windows.Forms;
using MedicineSystem.Data;

namespace MedicineSystem
{
    static class Program
    {
        public static DataStore DataStore { get; private set; }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            DataStore = new DataStore();

            if (!DataStore.HasData())
            {
                DataInitializer.InitializeDefaultData(DataStore);
            }

            Application.Run(new Forms.MainForm());
        }
    }
}
