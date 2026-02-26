using System;
using System.Collections.Generic;

namespace MedicineSystem.Models
{
    public class Prescription
    {
        public int Id { get; set; }
        public string PatientName { get; set; }
        public int PatientAge { get; set; }
        public string PatientGender { get; set; }
        public string Diagnosis { get; set; }
        public decimal TotalAmount { get; set; }
        public string CreatedBy { get; set; }
        public DateTime CreatedAt { get; set; }
        public List<PrescriptionItem> Items { get; set; }

        public Prescription()
        {
            PatientName = "";
            PatientAge = 0;
            PatientGender = "男";
            Diagnosis = "";
            TotalAmount = 0;
            CreatedBy = "医生";
            CreatedAt = DateTime.Now;
            Items = new List<PrescriptionItem>();
        }
    }
}
