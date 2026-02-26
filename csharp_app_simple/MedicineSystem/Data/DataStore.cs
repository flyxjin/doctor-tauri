using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Web.Script.Serialization;
using MedicineSystem.Models;

namespace MedicineSystem.Data
{
    public class DataStore
    {
        private readonly string _dataPath;
        private List<Medicine> _medicines;
        private List<Inventory> _inventory;
        private List<Prescription> _prescriptions;
        private List<PrescriptionItem> _prescriptionItems;
        private List<InventoryHistory> _inventoryHistory;
        private List<OperationLog> _operationLogs;
        private readonly JavaScriptSerializer _serializer;

        private int _nextMedicineId = 1;
        private int _nextInventoryId = 1;
        private int _nextPrescriptionId = 1;
        private int _nextPrescriptionItemId = 1;
        private int _nextInventoryHistoryId = 1;
        private int _nextOperationLogId = 1;

        public DataStore()
        {
            _dataPath = GetDataPath();
            _serializer = new JavaScriptSerializer();
            _serializer.MaxJsonLength = int.MaxValue;
            
            _medicines = new List<Medicine>();
            _inventory = new List<Inventory>();
            _prescriptions = new List<Prescription>();
            _prescriptionItems = new List<PrescriptionItem>();
            _inventoryHistory = new List<InventoryHistory>();
            _operationLogs = new List<OperationLog>();
            
            LoadData();
        }

        private string GetDataPath()
        {
            string appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            string appDir = Path.Combine(appData, "MedicineSystem");
            
            if (!Directory.Exists(appDir))
            {
                Directory.CreateDirectory(appDir);
            }
            
            return appDir;
        }

        private void LoadData()
        {
            _medicines = LoadFromFile<List<Medicine>>("medicines.json") ?? new List<Medicine>();
            _inventory = LoadFromFile<List<Inventory>>("inventory.json") ?? new List<Inventory>();
            _prescriptions = LoadFromFile<List<Prescription>>("prescriptions.json") ?? new List<Prescription>();
            _prescriptionItems = LoadFromFile<List<PrescriptionItem>>("prescription_items.json") ?? new List<PrescriptionItem>();
            _inventoryHistory = LoadFromFile<List<InventoryHistory>>("inventory_history.json") ?? new List<InventoryHistory>();
            _operationLogs = LoadFromFile<List<OperationLog>>("operation_logs.json") ?? new List<OperationLog>();
            
            UpdateNextIds();
        }

        private T LoadFromFile<T>(string filename) where T : class
        {
            string filepath = Path.Combine(_dataPath, filename);
            if (File.Exists(filepath))
            {
                try
                {
                    string json = File.ReadAllText(filepath, Encoding.UTF8);
                    return _serializer.Deserialize<T>(json);
                }
                catch
                {
                    return null;
                }
            }
            return null;
        }

        private void SaveToFile<T>(string filename, T data)
        {
            string filepath = Path.Combine(_dataPath, filename);
            string json = _serializer.Serialize(data);
            File.WriteAllText(filepath, json, Encoding.UTF8);
        }

        private void UpdateNextIds()
        {
            foreach (var m in _medicines)
            {
                if (m.Id >= _nextMedicineId) _nextMedicineId = m.Id + 1;
            }
            foreach (var i in _inventory)
            {
                if (i.Id >= _nextInventoryId) _nextInventoryId = i.Id + 1;
            }
            foreach (var p in _prescriptions)
            {
                if (p.Id >= _nextPrescriptionId) _nextPrescriptionId = p.Id + 1;
            }
            foreach (var pi in _prescriptionItems)
            {
                if (pi.Id >= _nextPrescriptionItemId) _nextPrescriptionItemId = pi.Id + 1;
            }
        }

        public void SaveAll()
        {
            SaveToFile("medicines.json", _medicines);
            SaveToFile("inventory.json", _inventory);
            SaveToFile("prescriptions.json", _prescriptions);
            SaveToFile("prescription_items.json", _prescriptionItems);
            SaveToFile("inventory_history.json", _inventoryHistory);
            SaveToFile("operation_logs.json", _operationLogs);
        }

        public List<Medicine> Medicines { get { return _medicines; } }
        public List<Inventory> Inventory { get { return _inventory; } }
        public List<Prescription> Prescriptions { get { return _prescriptions; } }
        public List<PrescriptionItem> PrescriptionItems { get { return _prescriptionItems; } }
        public List<InventoryHistory> InventoryHistory { get { return _inventoryHistory; } }
        public List<OperationLog> OperationLogs { get { return _operationLogs; } }

        public int AddMedicine(Medicine medicine)
        {
            medicine.Id = _nextMedicineId++;
            medicine.CreatedAt = DateTime.Now;
            medicine.UpdatedAt = DateTime.Now;
            _medicines.Add(medicine);
            SaveAll();
            return medicine.Id;
        }

        public void UpdateMedicine(Medicine medicine)
        {
            var existing = _medicines.FirstOrDefault(m => m.Id == medicine.Id);
            if (existing != null)
            {
                _medicines.Remove(existing);
                medicine.UpdatedAt = DateTime.Now;
                _medicines.Add(medicine);
                SaveAll();
            }
        }

        public void DeleteMedicine(int id)
        {
            _medicines.RemoveAll(m => m.Id == id);
            _inventory.RemoveAll(i => i.MedicineId == id);
            SaveAll();
        }

        public Medicine GetMedicineById(int id)
        {
            return _medicines.FirstOrDefault(m => m.Id == id);
        }

        public Medicine GetMedicineByName(string name)
        {
            return _medicines.FirstOrDefault(m => m.Name == name);
        }

        public List<Medicine> SearchMedicines(string keyword, string category = null, string nature = null)
        {
            var result = _medicines.AsEnumerable();
            
            if (!string.IsNullOrEmpty(keyword))
            {
                result = result.Where(m => 
                    m.Name.Contains(keyword) || 
                    m.Alias.Contains(keyword) || 
                    m.Efficacy.Contains(keyword));
            }
            
            if (!string.IsNullOrEmpty(category) && category != "全部分类")
            {
                result = result.Where(m => m.Category == category);
            }
            
            if (!string.IsNullOrEmpty(nature) && nature != "全部药性")
            {
                result = result.Where(m => m.Nature == nature);
            }
            
            return result.ToList();
        }

        public void AddInventory(Inventory inventory)
        {
            inventory.Id = _nextInventoryId++;
            inventory.CreatedAt = DateTime.Now;
            inventory.UpdatedAt = DateTime.Now;
            _inventory.Add(inventory);
            SaveAll();
        }

        public void UpdateInventory(Inventory inventory)
        {
            var existing = _inventory.FirstOrDefault(i => i.MedicineId == inventory.MedicineId);
            if (existing != null)
            {
                _inventory.Remove(existing);
                inventory.UpdatedAt = DateTime.Now;
                _inventory.Add(inventory);
                SaveAll();
            }
        }

        public Inventory GetInventoryByMedicineId(int medicineId)
        {
            return _inventory.FirstOrDefault(i => i.MedicineId == medicineId);
        }

        public void StockIn(int medicineId, decimal quantity, decimal price, string notes)
        {
            var inventory = GetInventoryByMedicineId(medicineId);
            var medicine = GetMedicineById(medicineId);
            
            if (inventory != null && medicine != null)
            {
                inventory.Quantity += quantity;
                inventory.Price = price;
                inventory.UpdatedAt = DateTime.Now;
                
                var history = new InventoryHistory
                {
                    MedicineId = medicineId,
                    MedicineName = medicine.Name,
                    Type = "入库",
                    Quantity = quantity,
                    Price = price,
                    TotalAmount = quantity * price,
                    Notes = notes
                };
                AddInventoryHistory(history);
                
                SaveAll();
            }
        }

        public void StockOut(int medicineId, decimal quantity, string notes)
        {
            var inventory = GetInventoryByMedicineId(medicineId);
            var medicine = GetMedicineById(medicineId);
            
            if (inventory != null && medicine != null)
            {
                inventory.Quantity -= quantity;
                inventory.UpdatedAt = DateTime.Now;
                
                var history = new InventoryHistory
                {
                    MedicineId = medicineId,
                    MedicineName = medicine.Name,
                    Type = "出库",
                    Quantity = quantity,
                    Price = inventory.Price,
                    TotalAmount = quantity * inventory.Price,
                    Notes = notes
                };
                AddInventoryHistory(history);
                
                SaveAll();
            }
        }

        public int AddPrescription(Prescription prescription)
        {
            prescription.Id = _nextPrescriptionId++;
            prescription.CreatedAt = DateTime.Now;
            _prescriptions.Add(prescription);
            
            foreach (var item in prescription.Items)
            {
                item.Id = _nextPrescriptionItemId++;
                item.PrescriptionId = prescription.Id;
                _prescriptionItems.Add(item);
                
                StockOut(item.MedicineId, item.Quantity, $"处方销售-{prescription.Id}");
            }
            
            SaveAll();
            return prescription.Id;
        }

        public void DeletePrescription(int id)
        {
            _prescriptions.RemoveAll(p => p.Id == id);
            _prescriptionItems.RemoveAll(pi => pi.PrescriptionId == id);
            SaveAll();
        }

        public Prescription GetPrescriptionById(int id)
        {
            var prescription = _prescriptions.FirstOrDefault(p => p.Id == id);
            if (prescription != null)
            {
                prescription.Items = _prescriptionItems.Where(pi => pi.PrescriptionId == id).ToList();
            }
            return prescription;
        }

        public List<PrescriptionItem> GetPrescriptionItems(int prescriptionId)
        {
            return _prescriptionItems.Where(pi => pi.PrescriptionId == prescriptionId).ToList();
        }

        public void AddInventoryHistory(InventoryHistory history)
        {
            history.Id = _nextInventoryHistoryId++;
            history.CreatedAt = DateTime.Now;
            _inventoryHistory.Add(history);
        }

        public void AddOperationLog(OperationLog log)
        {
            log.Id = _nextOperationLogId++;
            log.CreatedAt = DateTime.Now;
            _operationLogs.Add(log);
            SaveAll();
        }

        public bool HasData()
        {
            return _medicines.Count > 0;
        }

        public int GetMedicineCount()
        {
            return _medicines.Count;
        }

        public decimal GetTotalInventoryValue()
        {
            return _inventory.Sum(i => i.Quantity * i.Price);
        }

        public int GetLowStockCount()
        {
            return _inventory.Count(i => i.Quantity <= i.MinStock);
        }

        public List<Inventory> GetLowStockItems()
        {
            return _inventory.Where(i => i.Quantity <= i.MinStock).ToList();
        }

        public void Backup()
        {
            string backupDir = Path.Combine(_dataPath, "backups");
            if (!Directory.Exists(backupDir))
            {
                Directory.CreateDirectory(backupDir);
            }
            
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            string backupPath = Path.Combine(backupDir, $"backup_{timestamp}");
            Directory.CreateDirectory(backupPath);
            
            File.Copy(Path.Combine(_dataPath, "medicines.json"), Path.Combine(backupPath, "medicines.json"), true);
            File.Copy(Path.Combine(_dataPath, "inventory.json"), Path.Combine(backupPath, "inventory.json"), true);
            File.Copy(Path.Combine(_dataPath, "prescriptions.json"), Path.Combine(backupPath, "prescriptions.json"), true);
            File.Copy(Path.Combine(_dataPath, "prescription_items.json"), Path.Combine(backupPath, "prescription_items.json"), true);
        }
    }
}
