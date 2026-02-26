using System;

namespace MedicineSystem.Models
{
    public class OperationLog
    {
        public int Id { get; set; }
        public string OperationType { get; set; }
        public string TargetType { get; set; }
        public int TargetId { get; set; }
        public string Operator { get; set; }
        public string Details { get; set; }
        public DateTime CreatedAt { get; set; }

        public OperationLog()
        {
            OperationType = "";
            TargetType = "";
            Operator = "系统管理员";
            Details = "";
            CreatedAt = DateTime.Now;
        }
    }
}
