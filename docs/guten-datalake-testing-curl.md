### **🚀 `cURL` Commands to Test `guten-datalake` APIs**

Below are **cURL commands** to test each API endpoint in `guten-datalake`.  
Make sure the **FastAPI server is running** before testing:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

---

## **📌 1️⃣ Get All Sites**
```bash
curl -X GET "http://localhost:8005/guten/sites" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
[
  {
    "id": 1,
    "name": "adaprise_com",
    "title": "Adaptive Enterprise"
  },
  {
    "id": 2,
    "name": "tiers_ai",
    "title": "Tiers AI Platform"
  }
]
```

---

## **📌 2️⃣ Get a Single Site by Name**
```bash
curl -X GET "http://localhost:8005/guten/sites/adaprise_com" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
{
  "id": 1,
  "name": "adaprise_com",
  "title": "Adaptive Enterprise"
}
```

---

## **📌 3️⃣ Get All Sections for a Site**
```bash
curl -X GET "http://localhost:8005/guten/sections?site=adaprise_com" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
[
  {
    "id": 1,
    "site_id": 1,
    "name": "business",
    "title": "Business Strategy"
  },
  {
    "id": 2,
    "site_id": 1,
    "name": "science",
    "title": "Scientific Research"
  }
]
```

---

## **📌 4️⃣ Get a Single Section**
```bash
curl -X GET "http://localhost:8005/guten/sections/business?site=adaprise_com" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
{
  "id": 1,
  "site_id": 1,
  "name": "business",
  "title": "Business Strategy"
}
```

---

## **📌 5️⃣ Create a New Section**
```bash
curl -X POST "http://localhost:8005/guten/sections" -H "Content-Type: application/json" -d '{
  "site_id": 1,
  "name": "tech",
  "title": "Technology Trends"
}'
```

✅ **Expected Response:**
```json
{
  "id": 3,
  "site_id": 1,
  "name": "tech",
  "title": "Technology Trends"
}
```

---

## **📌 6️⃣ Get All Pages in a Section**
```bash
curl -X GET "http://localhost:8005/guten/pages?section=science" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
[
  {
    "id": 1,
    "section_id": 2,
    "name": "quantum",
    "title": "Quantum Computing",
    "abstract": "Understanding the future of quantum tech.",
    "content": "Quantum computing revolutionizes..."
  },
  {
    "id": 2,
    "section_id": 2,
    "name": "ai",
    "title": "Artificial Intelligence",
    "abstract": "Latest trends in AI and ML.",
    "content": "AI is transforming..."
  }
]
```

---

## **📌 7️⃣ Get a Single Page**
```bash
curl -X GET "http://localhost:8005/guten/pages/quantum?section=science" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
{
  "id": 1,
  "section_id": 2,
  "name": "quantum",
  "title": "Quantum Computing",
  "abstract": "Understanding the future of quantum tech.",
  "content": "Quantum computing revolutionizes..."
}
```

---

## **📌 8️⃣ Create a New Page**
```bash
curl -X POST "http://localhost:8005/guten/pages" -H "Content-Type: application/json" -d '{
  "section_id": 2,
  "name": "ml",
  "title": "Machine Learning",
  "abstract": "Exploring deep learning advancements.",
  "content": "Deep learning is making AI smarter..."
}'
```

✅ **Expected Response:**
```json
{
  "id": 3,
  "section_id": 2,
  "name": "ml",
  "title": "Machine Learning",
  "abstract": "Exploring deep learning advancements.",
  "content": "Deep learning is making AI smarter..."
}
```

---

## **📌 9️⃣ Publish a Site**
```bash
curl -X POST "http://localhost:8005/guten/publish/adaprise_com" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
{
  "message": "Site adaprise_com successfully published."
}
```

---

## **📌 🔟 Get a Published Page**
```bash
curl -X GET "http://localhost:8005/guten/published/pages/quantum?site=adaprise_com" -H "Content-Type: application/json"
```

✅ **Expected Response:**
```json
{
  "id": 1,
  "section_id": 2,
  "name": "quantum",
  "title": "Quantum Computing",
  "abstract": "Understanding the future of quantum tech.",
  "content": "Quantum computing revolutionizes..."
}
```

---

## **🚀 Next Steps**
1️⃣ **Would you like authentication (JWT) for `POST /pages` & `POST /sections`?**  
2️⃣ **Would you like `PUT` & `DELETE` APIs for updating/removing content?**  
3️⃣ **Would you like a `GET /search?q=ai` API to search across pages?**  

