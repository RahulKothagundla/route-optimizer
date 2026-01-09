# 🚀 Complete Setup Guide

## ⏱️ Total Time: 10 Minutes

Follow these steps exactly to get your Route Optimizer running.

---

## ✅ Step 1: Prerequisites Check (2 min)

### **1.1 Check Python Version**

```bash
python --version
# or
python3 --version
```

**Required:** Python 3.9 or higher

If not installed:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **Mac:** `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

### **1.2 Check Git**

```bash
git --version
```

If not installed:
- **Windows:** Download from [git-scm.com](https://git-scm.com/)
- **Mac:** `brew install git`
- **Linux:** `sudo apt install git`

---

## 📁 Step 2: Clone Repository (1 min)

### **Option A: If you have the GitHub repo**

```bash
# Clone from GitHub
git clone https://github.com/RahulKothagundla/route-optimizer.git
cd route-optimizer
```

### **Option B: Create from scratch (Manual Setup)**

```bash
# Create project directory
mkdir route-optimizer
cd route-optimizer

# Initialize git
git init

# Create folder structure
mkdir -p data src/utils src/algorithms src/visualization tests
```

Then **copy all the files** I provided into their respective folders.

---

## 🔧 Step 3: Create Virtual Environment (2 min)

### **Why Virtual Environment?**
Keeps project dependencies isolated from your system Python.

### **Create and Activate**

**On Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

**On Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Verify Activation**

Your terminal prompt should now show `(venv)` at the beginning:
```
(venv) username@computer:~/route-optimizer$
```

---

## 📦 Step 4: Install Dependencies (3 min)

### **4.1 Upgrade pip (Optional but Recommended)**

```bash
pip install --upgrade pip
```

### **4.2 Install All Requirements**

```bash
pip install -r requirements.txt
```

This installs:
- streamlit (UI framework)
- pandas (data handling)
- numpy (calculations)
- folium (maps)
- plotly (charts)
- scikit-learn (ML algorithms)
- And more...

**Expected output:**
```
Successfully installed streamlit-1.31.0 pandas-2.1.4 numpy-1.26.3 ...
```

### **4.3 Verify Installation**

```bash
# Check Streamlit
streamlit --version

# Should output: Streamlit, version 1.31.0
```

---

## 📄 Step 5: Verify Data Files (1 min)

Check that these files exist:

```bash
# List data files
ls data/

# Should show:
# hyderabad_addresses.csv
# warehouse.json
```

If missing, **copy the CSV and JSON** I provided into the `data/` folder.

### **Quick Validation**

```bash
# Count addresses in CSV
wc -l data/hyderabad_addresses.csv

# Should output: 61 (60 addresses + 1 header)
```

---

## 🚀 Step 6: Run the App (1 min)

### **6.1 Start Streamlit**

```bash
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### **6.2 App Should Open Automatically**

Your browser will open to `http://localhost:8501`

You should see:
- ✅ "Smart Route Optimizer" header
- ✅ "Loaded 60 delivery addresses" success message
- ✅ Interactive map with colored markers
- ✅ Statistics and charts

---

## ✅ Step 7: Verify Everything Works

### **Test Checklist:**

1. **📍 Overview Tab:**
   - [ ] Shows "60" total addresses
   - [ ] Shows 4 localities
   - [ ] Bar chart displays properly

2. **🗺️ Map View Tab:**
   - [ ] Map loads and displays
   - [ ] Red warehouse marker visible
   - [ ] Blue/Green/Purple/Orange delivery markers visible
   - [ ] Can click markers for details

3. **📊 Statistics Tab:**
   - [ ] Shows distance metrics (min, max, avg)
   - [ ] Pie chart displays
   - [ ] Bar chart displays

4. **🧮 Distance Calculator Tab:**
   - [ ] Can select two locations
   - [ ] "Calculate" button works
   - [ ] Shows distance, time, cost
   - [ ] Mini-map displays route

If ALL checkboxes are ✅, you're ready for Day 2! 🎉

---

## 🐛 Troubleshooting

### **Issue 1: Module not found error**

```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
# Make sure venv is activated (you should see (venv) in prompt)
# If not, activate it again:
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall
pip install -r requirements.txt
```

---

### **Issue 2: File not found error**

```
FileNotFoundError: data/hyderabad_addresses.csv not found
```

**Solution:**
```bash
# Check your current directory
pwd  # Should be in route-optimizer/

# Check if data folder exists
ls data/

# If missing, create it
mkdir data

# Then copy the CSV and JSON files into data/
```

---

### **Issue 3: Map not displaying**

**Solution 1:** Clear Streamlit cache
```bash
streamlit cache clear
```

**Solution 2:** Restart Streamlit
```bash
# Press Ctrl+C to stop
# Then run again:
streamlit run app.py
```

---

### **Issue 4: Port already in use**

```
OSError: [Errno 48] Address already in use
```

**Solution:** Use a different port
```bash
streamlit run app.py --server.port 8502
```

---

### **Issue 5: Python version error**

```
ERROR: Package requires Python '>=3.9'
```

**Solution:** Upgrade Python
- Download latest Python from python.org
- Or use pyenv to manage multiple versions:
```bash
# Install pyenv (Mac/Linux)
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0

# Recreate venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Testing Your Setup

Run these commands to verify everything:

### **Test 1: Import Check**

```bash
python -c "from src.utils.helpers import haversine_distance; print('✅ Helpers OK')"
python -c "from src.utils.geocoding import load_addresses; print('✅ Geocoding OK')"
```

### **Test 2: Data Loading Test**

```bash
python -c "
from src.utils.geocoding import load_addresses, load_warehouse
df = load_addresses()
warehouse = load_warehouse()
print(f'✅ Loaded {len(df)} addresses')
print(f'✅ Warehouse: {warehouse[\"name\"]}')
"
```

### **Test 3: Distance Calculation Test**

```bash
python -c "
from src.utils.helpers import haversine_distance
dist = haversine_distance(17.4485, 78.3908, 17.4400, 78.3811)
print(f'✅ Distance calculation works: {dist:.2f} km')
"
```

**All tests pass?** You're good to go! 🚀

---

## 📚 Next Steps

Once setup is complete:

1. **Explore the app** - Click through all tabs
2. **Try the distance calculator** - Calculate some routes
3. **Check the code** - Open `src/utils/helpers.py` and read the functions
4. **Get ready for Day 2** - We'll implement TSP algorithms tomorrow!

---

## 🆘 Still Having Issues?

If you're stuck after trying all troubleshooting steps:

1. **Check Python path:**
   ```bash
   which python  # Mac/Linux
   where python  # Windows
   ```

2. **Reinstall from scratch:**
   ```bash
   # Deactivate venv
   deactivate
   
   # Remove old venv
   rm -rf venv/
   
   # Start over from Step 3
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Check for typos in filenames:**
   - File names are case-sensitive on Mac/Linux
   - Make sure `hyderabad_addresses.csv` (not `Hyderabad_addresses.csv`)

---

## ✅ Success Checklist

Before moving to Day 2, confirm:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` shows 20+ packages)
- [ ] Data files present in `data/` folder
- [ ] Streamlit app runs without errors
- [ ] All 4 tabs display correctly
- [ ] Map shows 60+ markers
- [ ] Distance calculator works

**All checked?** Congratulations! 🎉 You're ready for Day 2!

---

## 💡 Pro Tips

1. **Keep venv activated:** Always run `source venv/bin/activate` when working on the project

2. **Use a good code editor:**
   - VS Code (recommended): Free, great for Python
   - PyCharm Community: Powerful IDE
   - Cursor: AI-powered editor

3. **Git workflow:**
   ```bash
   # After setup, commit everything
   git add .
   git commit -m "Initial setup - Day 1 complete"
   git push origin main
   ```

4. **Create a GitHub repo:**
   - Go to github.com/new
   - Name: `route-optimizer`
   - Push your code:
   ```bash
   git remote add origin https://github.com/RahulKothagundla/route-optimizer.git
   git push -u origin main
   ```

---

**🎊 Setup Complete! Let's build something awesome tomorrow!**