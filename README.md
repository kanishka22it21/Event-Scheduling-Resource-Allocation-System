#  Event Scheduling & Resource Allocation System

A web-based application developed using **Flask** that allows organizations to schedule events, manage shared resources, allocate them efficiently, detect conflicts, and generate resource utilization reports.

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap
- **Tools:** VS Code, GitHub

---

## ✨ Features

- Create, view, and delete events  
- Add, edit, and delete resources  
- Allocate resources to events  
- Automatic conflict detection for overlapping events  
- Clear conflict display page  
- Resource utilization report based on date range  
- Clean and responsive Bootstrap UI  

---

## 🧠 Conflict Detection Logic

A conflict occurs when the same resource is assigned to two events whose time intervals overlap.

This logic handles:
- Partial overlaps
- Fully nested events
- Edge-case time boundaries

---

##Steps to run the project 

---

Step 1: Clone the Repository
```bash
git clone https://github.com/kanishka22it21/Event-Scheduling-Resource-Allocation-System.git
cd Event_Scheduling_Resource_Allocation_System




