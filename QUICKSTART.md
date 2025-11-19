# 🚀 Quickstart Guide

## ⚡ 3 Steps to Get Started

### 1️⃣ Configuration (1 minute)

Create a `.env` file at the root of your project:

```bash
OPENAI_API_KEY=sk-your-key-here
SERP_API_KEY=your-serp-key-here
```

### 2️⃣ Preparation (1 minute)

Place your PDF files in the `data/` folder:

```
data/
├── law_proposal_1.pdf
├── law_proposal_2.pdf
└── ...
```

### 3️⃣ Launch (30 seconds)

```bash
# (Optional but recommended) Run the test script
python test_rag.py

# Launch the app
streamlit run app.py
```

---

## 🎯 Using the Streamlit Interface

### First Use

1. **Click "🚀 Initialize Components"** (left sidebar)

   - Wait 5-10 seconds
   - You should see: "✅ Components initialized successfully!"

2. **Click "📥 Index PDFs from data/"** (left sidebar)

   - Wait 10-30 seconds (depending on the number of PDFs)
   - You should see: "✅ Indexing complete: X chunks added..."

3. **Ask your first question** (main input field)
   - Example: "What are the main objectives of this law proposal?"
   - Click "🔍 Send"
   - Wait 5-10 seconds
   - You will see the answer with cited sources!

### Subsequent Uses

**No need to re-initialize or re-index!**

Just run:

```bash
streamlit run app.py
```

And ask your questions directly.

---

## 🔍 Example Questions

### For a single law proposal

```
✅ "What is the main objective of this proposal?"
✅ "Who are the authors of this law proposal?"
✅ "Which articles are modified?"
✅ "What is the planned timeline?"
✅ "What are the financial impacts?"
```

### For comparing multiple documents

```
✅ "What are the differences between the proposals?"
✅ "Which topics are common across the documents?"
✅ "Summarize the main measures proposed"
```

---

## 🐛 Common Issues

### ❌ "OPENAI_API_KEY not found"

**Solution:** Check your `.env` file at the project root

### ❌ "Components not initialized"

**Solution:** Click "🚀 Initialize Components" in the sidebar

### ❌ "No relevant documents found"

**Solution:**

1. Make sure you have PDFs in `data/`
2. Click "📥 Index PDFs"

### ❌ App won't start

**Solution:**

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Relaunch
streamlit run app.py
```

---

## 📊 Verify Everything Works

### Automated Test

```bash
python test_rag.py
```

You should see:

```
✅ Test 1: Imports... OK
✅ Test 2: API Keys... OK
✅ Test 3: Initialization... OK
...
🎉 All tests passed!
```

---

## 💡 Tips

### Improve Answer Quality

1. **More context:** Increase `k` in `rag.py`
   ```python
   retriever = vectorstore.as_retriever(search_kwargs={"k": 10})  # Instead of 5
   ```
2. **Smaller chunks:** Reduce `chunk_size` for more precision
   ```python
   chunk_size=500,  # Instead of 1000
   ```
3. **Ask specific questions:** Specific questions yield better answers

### Completely Reset the Index

If you want to erase everything and start over:

1. In the sidebar, check "⚠️ Confirm deletion"
2. Click "🔄 Clear index"
3. Re-index your documents

Or manually delete:

```bash
# Windows PowerShell
Remove-Item -Recurse -Force data/qdrant_db

# Relaunch the app
streamlit run app.py
```

---

## 📚 Full Documentation

- **System architecture:** See `ARCHITECTURE.md`
- **Correction details:** See `CORRECTIONS.md`
- **Commented source code:** See `rag.py`

---

## 🎓 How the System Works

```
Your question
      ↓
Converted to vector (embedding)
      ↓
Search in Qdrant (5 closest chunks)
      ↓
Context construction
      ↓
Sent to LLM (GPT-4) with context
      ↓
Answer generated
      ↓
Sources cited
      ↓
Displayed in Streamlit
```

**Total time: ~10 seconds**

---

## ✅ Startup Checklist

- [ ] `.env` file created with API keys
- [ ] PDFs placed in the `data/` folder
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests passed (`python test_rag.py`)
- [ ] App launched (`streamlit run app.py`)
- [ ] Components initialized (sidebar button)
- [ ] Documents indexed (sidebar button)
- [ ] First question asked successfully!

---

**🎉 You're ready! Enjoy your RAG system for analyzing law proposals!**
