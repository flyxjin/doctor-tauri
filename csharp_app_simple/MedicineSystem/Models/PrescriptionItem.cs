using System;

namespace MedicineSystem.Models
{
    public class PrescriptionItem
    {
        public int Id { get; set; }
        public int PrescriptionId { get; set; }
        public int MedicineId { get; set; }
        public string MedicineName { get; set; }
        public decimal Quantity { get; set; }
        public string Unit { get; set; }
        public decimal Price { get; set; }
        public decimal Amount { get; set; }

        public PrescriptionItem()
        {
            MedicineName = "";
            Quantity = 0;
            Unit = "g";
            Price = 0;
            Amount = 0;
        }
    }
}
