## **📌 API Endpoints (for `guten-crust`)**
The following APIs will be implemented in **FastAPI (`guten-datalake`)** and consumed by `guten-crust`:

### **1️⃣ Site Data APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/guten/sites` | Fetch all sites |
| `GET`  | `/guten/sites/{site_name}` | Fetch a single site by name |

### **2️⃣ Section (Navigation) APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/guten/sections?site={site_name}` | Get all sections of a site |
| `GET`  | `/guten/sections/{section_name}?site={site_name}` | Get section details |
| `POST` | `/guten/sections` | Create a new section |
| `PUT`  | `/guten/sections/{section_id}` | Update section details |
| `DELETE` | `/guten/sections/{section_id}` | Delete a section |

### **3️⃣ Page Content APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/guten/pages?section={section_name}` | Get pages in a section |
| `GET`  | `/guten/pages/{page_name}?section={section_name}` | Get page details |
| `POST` | `/guten/pages` | Create a new page |
| `PUT`  | `/guten/pages/{page_id}` | Update a page |
| `DELETE` | `/guten/pages/{page_id}` | Delete a page |

### **4️⃣ Publishing APIs**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/guten/publish/{site_name}` | Publish a site |
| `GET`  | `/guten/published/pages/{page_name}?site={site_name}` | Get published page |

---
## Updated ...
---

| Method | Endpoint                                           | Action                       |
|--------|----------------------------------------------------|------------------------------|
| GET    | `/guten/sites`                                     | Fetch all sites              |
| GET    | `/guten/sites/{site_name}`                         | Fetch one site               |
| POST   | `/guten/sites`                                     | Create new site              |
| GET    | `/guten/sections?site={site_name}`                 | Get sections for site        |
| GET    | `/guten/sections/{section_name}?site={site_name}`  | Get section details          |
| POST   | `/guten/sections`                                  | Create new section           |
| PUT    | `/guten/sections/{section_id}`                     | Update section               |
| DELETE | `/guten/sections/{section_id}`                     | Delete section               |
| GET    | `/guten/pages?section={section_name}`              | Get pages for section        |
| GET    | `/guten/pages/{page_name}?section={section_name}`  | Get page details             |
| POST   | `/guten/pages`                                     | Create page                  |
| PUT    | `/guten/pages/{page_id}`                           | Update page                  |
| DELETE | `/guten/pages/{page_id}`                           | Delete page                  |
| POST   | `/guten/publish/{site_name}`                       | Publish site                 |
| GET    | `/guten/published/pages/{page_name}?site={site}`   | Fetch published page         |

---
## Updated ...
---

| Method | Endpoint                                           | Description                             |
|--------|----------------------------------------------------|-----------------------------------------|
| GET    | `/guten/pages?site={site_name}&section={section_name}`             | Get pages for a specific section of a site|
| GET    | `/guten/pages/{page_name}?site={site_name}&section={section_name}` | Get page details within a section/site  |
| GET    | `/guten/sections?site={site_name}`                                | Get all sections for a site             |
| GET    | `/guten/sections/{section_name}?site={site_name}`                 | Get section details                     |

