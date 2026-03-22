# Data Folder — The Engine Room 🚂🗃️

The `data/` directory stores all persistent knowledge in the Resilienz.AI platform. It follows a **Hybrid Strategy** (Fact-based SQL + Semantic Vector DB).

## 📄 Key Components

| File | Purpose |
|------|---------|
| `resilienz.db` | **The SQL Fact Layer**: SQLite database containing orders, inventory, and supplier master data. |
| `vector_store/` | **The Semantic Memory**: ChromaDB storage for global events and unstructured news. |
| `map_data.py` | **Geographic Intelligence**: Maps city-level supplier data to absolute Lat/Long coordinates for the Peak Map. |
| `generate_data.py` | **The Data Heart**: Synthetically builds all CSV files and populates both databases. |

## 🧪 Peak Demo: Scenario Stability
For the Stress-Test Center, the data layer utilizes a "Shadow Data" layer in the API. This allows for complex simulations without corrupting the stable, golden-copy values in the `resilienz.db`.

---

*For technical schema details, refer to [2_data_architecture.md](../documentation/2_data_architecture.md).*
