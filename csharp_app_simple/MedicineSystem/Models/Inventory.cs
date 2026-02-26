using System;

namespace MedicineSystem.Models
{
    public class Inventory
    {
        public int Id { get; set; }
        public int MedicineId { get; set; }
        public string MedicineName { get; set; }
        public decimal Quantity { get; set; }
        public string Unit { get; set; }
        public decimal Price { get; set; }
        public decimal MinStock { get; set; }
        public string Notes { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }

        public Inventory()
        {
            MedicineName = "";
            Quantity = 0;
            Unit = "g";
            Price = 0;
            MinStock = 10;
            Notes = "";
            CreatedAt = DateTime.Now;
            UpdatedAt = DateTime.Now;
        }
    }
}
