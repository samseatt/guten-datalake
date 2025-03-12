# Guten Datalake

Guten Datalake is a FastAPI-based microservice that serves as the backend data store for the Guten platform. It provides a RESTful API for managing and retrieving site, section, page, and publishing data stored in PostgreSQL.

## 📌 Features
- CRUD operations for sites, sections, and pages.
- Publishing workflow for drafting and publishing sites.
- Supports Markdown-based content.
- Utilizes PostgreSQL as the primary database.
- Authentication-ready architecture (integration with an auth service planned).

## 📂 Project Structure
```
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── sites.py
│   │   │   ├── sections.py
│   │   │   ├── pages.py
│   │   │   ├── publish.py
│   │   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   ├── models/
│   │   ├── site.py
│   │   ├── section.py
│   │   ├── page.py
│   │   ├── publish.py
│   ├── crud/
│   │   ├── site.py
│   │   ├── section.py
│   │   ├── page.py
│   │   ├── publish.py
│   ├── schemas/
│   │   ├── site.py
│   │   ├── section.py
│   │   ├── page.py
│   │   ├── publish.py
├── scripts/
│   ├── database/
│   │   ├── schema.sql
├── tests/
│   ├── test_sites.py
│   ├── test_sections.py
│   ├── test_pages.py
├── requirements.in
├── requirements.txt
├── README.md
```

## 🚀 Installation

### 1️⃣ Prerequisites
- Python 3.10+
- PostgreSQL (Configured with schemas `draft` and `published`)
- `pip` and `venv` for package management

### 2️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo/guten-datalake.git
cd guten-datalake
```

### 3️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 4️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 5️⃣ Configure Environment Variables
Create a `.env` file in the root directory with:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/guten_datalake
```

### 6️⃣ Apply Database Schema
```sh
psql -d guten_datalake -f scripts/database/schema.sql
```

### 7️⃣ Run the Application
```sh
uvicorn src.api.main:app --host 0.0.0.0 --port 8005 --reload
```

### 8️⃣ Run Tests
```sh
pytest tests/
```

## 🔥 API Endpoints

### 1️⃣ Site Management
- **GET** `/guten/sites` - Get all sites
- **POST** `/guten/sites` - Create a new site
- **PUT** `/guten/sites/{site_name}` - Update a site
- **DELETE** `/guten/sites/{site_name}` - Delete a site

### 2️⃣ Section Management
- **GET** `/guten/sections?site={site_name}` - Get all sections for a site
- **POST** `/guten/sections` - Create a section
- **PUT** `/guten/sections/{section_id}` - Update a section
- **DELETE** `/guten/sections/{section_id}` - Delete a section

### 3️⃣ Page Management
- **GET** `/guten/pages?site={site_name}&section={section_name}` - Get pages in a section
- **POST** `/guten/pages` - Create a page
- **PUT** `/guten/pages/{page_id}` - Update a page
- **DELETE** `/guten/pages/{page_id}` - Delete a page

### 4️⃣ Publishing
- **POST** `/guten/publish/{site_name}` - Publish a site
- **GET** `/guten/published/pages/{page_name}?site={site_name}` - Get a published page

## 🛠️ Technologies Used
- **FastAPI** - Web framework
- **PostgreSQL** - Database
- **SQLAlchemy & Asyncpg** - ORM & async DB driver
- **Uvicorn** - ASGI Server
- **Pytest** - Testing

## 📜 License
MIT License

## 📞 Contact
For any issues, create a GitHub issue or reach out to samseatt@gmail.com.

