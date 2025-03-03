Here's a comprehensive and ready-to-use **curl test suite** to verify all endpoints of your **`guten-datalake`** API thoroughly.

✅ **Pre-requisite**:  
Make sure **FastAPI server** (`guten-datalake`) is running at:  
```
http://localhost:8005
```

---

## 🔷 **1. Sites API Tests**

### **1.1 Create a new site**
```bash
curl -X POST "http://localhost:8005/guten/sites" \
-H "Content-Type: application/json" \
-d '{"name": "acme_com", "title": "Acme Corp"}'
```

### **1.2 Fetch all sites**
```bash
curl "http://localhost:8005/guten/sites"
```

### **1.3 Fetch single site by name**
```bash
curl "http://localhost:8005/guten/sites/acme_com"
```

---

## 🔷 **2. Sections API Tests**

### **2.1 Create a new section**
```bash
curl -X POST "http://localhost:8005/guten/sections" \
-H "Content-Type: application/json" \
-d '{
  "site_id": "1",
  "name": "products",
  "title": "Products"
}'
```

### **2.2 Fetch all sections for a site**
```bash
curl "http://localhost:8005/guten/sections?site=acme_com"
```

### **2.3 Fetch single section details**
```bash
curl "http://localhost:8005/guten/sections/products?site=acme_com"
```

### **2.4 Update section details** *(replace `{section_id}` from above results)*
```bash
curl -X PUT "http://localhost:8005/guten/sections/1" \
-H "Content-Type: application/json" \
-d '{
  "site_id": "1",
  "name": "services",
  "title": "Our Services"
}'
```

### **2.5 Delete section**
```bash
curl -X DELETE "http://localhost:8005/guten/sections/1"
```

---

## 🔷 **3. Pages API Tests**

### **3.1 Create a new page**
```bash
curl -X POST "http://localhost:8005/guten/pages" \
-H "Content-Type: application/json" \
-d '{
  "section_id": "1",
  "name": "new_product",
  "title": "Our New Product",
  "abstract": "Introducing our innovative product.",
  "content": "Detailed description of the new product..."
}'
```

### **3.2 Fetch all pages in a section**
```bash
curl "http://localhost:8005/guten/pages?site_id=1&section=products"
```

### **3.3 Fetch page details**
```bash
curl "http://localhost:8005/guten/pages/new_product?site=acme_com&section=products"
```

### **3.4 Update a page** *(replace `{page_id}` from above results)*
```bash
curl -X PUT "http://localhost:8005/guten/pages/{page_id}" \
-H "Content-Type: application/json" \
-d '{
  "site_name": "acme_com",
  "section_name": "products",
  "name": "updated_product",
  "title": "Updated Product",
  "abstract": "Updated abstract.",
  "content": "Updated detailed content."
}'
```

### **3.5 Delete a page**
```bash
curl -X DELETE "http://localhost:8005/guten/pages/{page_id}"
```

---

## 🔷 **4. Publishing API Tests**

### **4.1 Publish a site**
```bash
curl -X POST "http://localhost:8005/guten/publish/acme_com"
```

### **4.2 Fetch a published page**
```bash
curl "http://localhost:8005/guten/published/pages/new_product?site=acme_com"
```

---

## 🚀 **Testing Flow Recommendation:**

Follow this sequence to comprehensively test your workflow:

- ✅ **Create Site** → Create **Sections** → Create **Pages**
- ✅ Test **GET** endpoints to verify **data integrity**
- ✅ Update & Delete individual resources
- ✅ Finally, test **Publish** workflow and retrieval of **published pages**

---

## 🚩 **Checklist Before Moving On**:

- [ ] All endpoints returning expected data
- [ ] Data correctly created, updated, and deleted
- [ ] Proper HTTP response codes (200, 201, 404, etc.)
- [ ] Error handling clear and correct

---

Once all ✅ tests are passing, your **`guten-datalake`** microservice is robust, and we can confidently proceed to implement **`guten-crust`**.

