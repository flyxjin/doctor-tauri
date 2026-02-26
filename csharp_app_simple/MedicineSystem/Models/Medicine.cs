using System;

namespace MedicineSystem.Models
{
    public class Medicine
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Alias { get; set; }
        public string Category { get; set; }
        public string Nature { get; set; }
        public string Taste { get; set; }
        public string Meridian { get; set; }
        public string Efficacy { get; set; }
        public string Indications { get; set; }
        public string Usage { get; set; }
        public string Dosage { get; set; }
        public string Contraindication { get; set; }
        public string Notes { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }

        public Medicine()
        {
            Name = "";
            Alias = "";
            Category = "";
            Nature = "";
            Taste = "";
            Meridian = "";
            Efficacy = "";
            Indications = "";
            Usage = "";
            Dosage = "";
            Contraindication = "";
            Notes = "";
            CreatedAt = DateTime.Now;
            UpdatedAt = DateTime.Now;
        }
    }
}
