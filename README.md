# ✦ SRI PAVANI JEWELLERY — INSTALLATION GUIDE
### Complete Beginner's Guide (Step by Step)

---

## 📁 PROJECT STRUCTURE

```
sri_pavani/
│
├── app.py                         ← Main Flask application (all routes & logic)
├── requirements.txt               ← Python packages to install
│
├── static/
│   ├── css/
│   │   └── style.css              ← All styling (dark/light theme)
│   ├── js/
│   │   └── main.js                ← Cart, animations, theme toggle
│   └── uploads/
│       ├── products/              ← Product images (auto-created)
│       ├── categories/            ← Category images (auto-created)
│       └── offers/                ← Offer/banner images (auto-created)
│
└── templates/
    ├── base.html                  ← Header, nav, footer shared template
    ├── index.html                 ← Homepage
    ├── login.html                 ← Sign in page
    ├── register.html              ← Create account page
    ├── profile.html               ← Customer profile & cart
    ├── edit_profile.html          ← Edit profile details
    ├── category.html              ← Single category product page
    ├── all_products.html          ← Browse all products
    ├── components/
    │   └── product_card.html      ← Reusable product card
    └── admin/
        ├── base_admin.html        ← Admin panel layout
        ├── dashboard.html         ← Admin home with stats
        ├── categories.html        ← Manage categories
        ├── products.html          ← Manage products
        ├── offers.html            ← Manage offers & banners
        └── customers.html        ← View all customers
```

---

## 🛠️ STEP 1 — INSTALL PYTHON

1. Go to **https://python.org/downloads**
2. Download Python 3.11 or newer
3. During installation, **CHECK the box** that says "Add Python to PATH" ← Very important!
4. Click Install Now
5. After install, open **Command Prompt** (press Win+R, type `cmd`, press Enter)
6. Type this and press Enter:
   ```
   python --version
   ```
   You should see something like: `Python 3.11.5`

---

## 🛠️ STEP 2 — INSTALL VS CODE (Code Editor)

1. Go to **https://code.visualstudio.com**
2. Download and install VS Code
3. Open VS Code
4. Press `Ctrl+Shift+X` to open Extensions
5. Search and install:
   - **Python** (by Microsoft) ← Required
   - **Flask Snippets** ← Optional but helpful

---

## 🛠️ STEP 3 — OPEN THE PROJECT IN VS CODE

1. Open VS Code
2. Click **File → Open Folder**
3. Navigate to your `sri_pavani` folder and click **Select Folder**
4. You should see all the project files in the left sidebar

---

## 🛠️ STEP 4 — OPEN THE TERMINAL IN VS CODE

In VS Code:
1. Click **Terminal** in the top menu
2. Click **New Terminal**
3. A terminal opens at the bottom of VS Code
4. Make sure you are inside the `sri_pavani` folder. You should see something like:
   ```
   C:\Users\YourName\sri_pavani>
   ```

---

## 🛠️ STEP 5 — CREATE A VIRTUAL ENVIRONMENT

A virtual environment keeps all your packages organized separately. Think of it as a clean room just for this project.

In the VS Code terminal, type:

**On Windows:**
```bash
python -m venv venv
```

Then activate it:
```bash
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ You'll know it worked when you see `(venv)` at the start of your terminal line.

---

## 🛠️ STEP 6 — INSTALL REQUIRED PACKAGES

With the virtual environment activated, type:
```bash
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, and everything else needed.

Wait for it to finish (might take 1-2 minutes).

---

## 🛠️ STEP 7 — RUN THE WEBSITE

In the terminal, type:
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## 🌐 STEP 8 — OPEN THE WEBSITE

1. Open any web browser (Chrome, Firefox, Edge)
2. Go to: **http://127.0.0.1:5000**
3. 🎉 Your Sri Pavani Jewellery website is live!

---

## 👑 ADMIN ACCESS

To access the Admin Panel:

1. Go to: **http://127.0.0.1:5000/login**
2. Sign in with:
   - **Email:** `admin@sripavani.com`
   - **Password:** `admin123`
3. After login, go to: **http://127.0.0.1:5000/admin**

### What Admin Can Do:
| Page | What You Can Do |
|------|----------------|
| Dashboard | See total products, customers, categories, offers |
| Categories | Add/remove categories with images, show/hide them |
| Products | Add products with images, mark as New/Best Seller, toggle stock |
| Offers | Upload offer banners with titles, show/hide offers |
| Customers | View all registered customers and their details |

---

## 🛒 HOW THE WEBSITE WORKS

| Feature | How It Works |
|---------|-------------|
| **Homepage** | Shows categories strip, offers, new collections, featured, best sellers |
| **Categories** | Scrollable boxes — number depends on what admin adds |
| **Add to Cart** | Click "+ Add" on any product — logged in users only |
| **Not Logged In?** | Popup appears asking to Sign In or Register |
| **Cart Badge** | Shows number of items in cart (top right) |
| **Dark/Light Mode** | Toggle the sun/moon icon in top right |
| **Mobile** | Hamburger menu appears on small screens |
| **Stock Out** | Admin marks product as Out of Stock — button gets disabled |

---

## 🎨 THEMES

| Theme | Colors |
|-------|--------|
| 🌑 **Dark Mode** | Black + Gold ombre — luxury look |
| 🌕 **Light Mode** | Teal + White — fresh & clean |

Users can toggle between themes using the ☀️/🌙 button. Their preference is saved automatically.

---

## 📱 MOBILE FRIENDLY

- Full responsive design for phones and tablets
- Hamburger menu on mobile
- Swipeable category strip
- Touch-friendly cart controls

---

## 🔧 COMMON ISSUES & FIXES

**Problem:** `python: command not found`
**Fix:** Reinstall Python and make sure "Add to PATH" is checked

---

**Problem:** `pip: command not found`
**Fix:** Type `python -m pip install -r requirements.txt` instead

---

**Problem:** Virtual environment not activating
**Fix:** Try running VS Code as Administrator (right-click VS Code → Run as Administrator)

---

**Problem:** Website shows error page
**Fix:** Check the terminal for error messages. Most common fix: make sure you're in the `sri_pavani` folder

---

**Problem:** Images not showing after upload
**Fix:** Make sure the `static/uploads/` folders exist (they auto-create on first run)

---

## 🗄️ DATABASE

The website automatically creates a database file called `sripavani.db` in your project folder when you first run it. This stores:
- All user accounts
- Products
- Categories  
- Cart items
- Offers

No extra setup needed — it works automatically!

---

## 🚀 TO STOP THE SERVER

Press **Ctrl + C** in the terminal.

## 🚀 TO START AGAIN

```bash
venv\Scripts\activate    (Windows)
python app.py
```

---

## ✦ QUICK COMMANDS SUMMARY

```bash
# 1. Open terminal in VS Code (Ctrl+`)
# 2. Activate virtual environment
venv\Scripts\activate

# 3. Start the server
python app.py

# 4. Open browser to:
http://127.0.0.1:5000

# Admin panel:
http://127.0.0.1:5000/admin
# Email: admin@sripavani.com | Password: admin123
```

---

*Sri Pavani Jewellery — Crafted With Divine Grace ✦*
