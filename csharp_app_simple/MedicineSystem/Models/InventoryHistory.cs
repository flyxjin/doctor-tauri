using System;

namespace MedicineSystem.Models
{
    public class InventoryHistory
    {
        public int Id { get; set; }
        public int MedicineId { get; set; }
        public string MedicineName { get; set; }
        public string Type { get; set; }
        public decimal Quantity { get; set; }
        public decimal Price { get; set; }
        public decimal TotalAmount { get; set; }
        public string Notes { get; set; }
        public DateTime CreatedAt { get; set; }

        public InventoryHistory()
        {
            MedicineName = "";
            Type = "";
            Quantity = 0;
            Price = 0;
            TotalAmount = 0;
            Notes = "";
            CreatedAt = DateTime.Now;
        }
    }
}
