# Rent vs. Buy Simulator — Setup Guide (README)

**Fisher College of Business — The Ohio State University**

This guide walks you through getting the Rent vs. Buy Simulator running on your Mac using Visual Studio Code. No programming experience needed.

---

## What This Program Is

A desktop financial tool that tells you whether you should rent or buy a home, based on your specific situation. It uses real finance concepts (NPV, IRR, opportunity cost) but presents everything in plain English with charts and color-coded results.

---

## What You Need Before Starting

- A Mac computer (macOS 10.15 or newer)
- An internet connection (for downloading software)
- About 10–15 minutes

---

## Step 1: Install Python

Python is the programming language this tool runs on. Your Mac may already have it, but we need the latest version.

1. Open your web browser
2. Go to **https://www.python.org/downloads/**
3. Click the big yellow **"Download Python 3.x.x"** button
4. Open the downloaded `.pkg` file from your Downloads folder
5. Click **Continue → Continue → Agree → Install**
6. Enter your Mac login password when prompted
7. Click **Install Software**
8. When it says "The installation was successful", click **Close**

**How to verify it worked:**
- Open the **Terminal** app (press `Cmd + Space`, type "Terminal", press Enter)
- Type `python3 --version` and press Enter
- You should see something like `Python 3.12.x` or `Python 3.13.x`

---

## Step 2: Install Visual Studio Code

VS Code is the application you'll use to open and run the program.

1. Go to **https://code.visualstudio.com**
2. Click the big blue **"Download for Mac"** button
3. Open your Downloads folder
4. Double-click the downloaded `.zip` file to unzip it
5. Drag the **Visual Studio Code** app into your **Applications** folder
6. Open it from Applications
7. If your Mac asks "Are you sure you want to open it?", click **Open**

---

## Step 3: Install the Python Extension in VS Code

This lets VS Code understand and run Python files.

1. Open **Visual Studio Code**
2. Look at the left sidebar — click the **Extensions icon** (it looks like four small squares, one detached)
3. In the search box at the top, type **Python**
4. The first result should be **"Python"** by **Microsoft** — it will have millions of downloads
5. Click the blue **Install** button
6. Wait about 30 seconds for it to finish

---

## Step 4: Install Required Libraries

The simulator uses three Python libraries for math and charts. You install them once and they stay on your computer.

1. In VS Code, go to the top menu bar: **Terminal → New Terminal**
2. A dark panel will appear at the bottom of the screen — this is your terminal
3. Copy and paste this entire line, then press **Enter**:

```
python3 -m pip install numpy numpy-financial matplotlib
```

4. Wait for it to finish. You'll see download progress and then "Successfully installed..." messages.

**If you get a permission error**, use this version instead:

```
python3 -m pip install --user numpy numpy-financial matplotlib
```

**If you see "command not found"**, Python may not be in your path. Close VS Code completely, reopen it, and try again. If it still doesn't work, restart your Mac, then try once more.

---

## Step 5: Download the Program File

1. Download the file **`rent_vs_buy.py`** (from wherever your group shared it — GitHub, Google Drive, email, etc.)
2. Save it somewhere easy to find, like your **Desktop** or a class folder
3. Remember where you put it

---

## Step 6: Open the File in VS Code

1. In VS Code, go to **File → Open...** (or press `Cmd + O`)
2. Navigate to where you saved `rent_vs_buy.py`
3. Select the file and click **Open**
4. You'll see the code appear in the editor — you don't need to read or understand it

---

## Step 7: Run It

1. Look at the **top-right corner** of the VS Code window
2. Click the **▶ (Play) button**
3. If VS Code asks you to select a Python interpreter, pick the one that says **Python 3.x.x**
4. The simulator will open as a **separate window** on your screen

You're done. The Rent vs. Buy Simulator is now running.

---

## How to Run It Again Later

1. Open **VS Code**
2. Go to **File → Open Recent** and pick `rent_vs_buy.py`
3. Click the **▶ Play button**

You do NOT need to reinstall anything. Steps 1–4 are one-time only.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"No module named numpy"** | Run `python3 -m pip install numpy numpy-financial matplotlib` in the VS Code terminal again |
| **Play button doesn't appear** | Make sure the Python extension is installed (Step 3). Restart VS Code. |
| **"command not found: python3"** | Reinstall Python from python.org. Restart VS Code after installing. |
| **Window is blank or tiny** | Drag the window corners to resize. Make sure you clicked RUN SIMULATION. |
| **"python3 -m pip" gives errors** | Try `pip3 install numpy numpy-financial matplotlib` instead |
| **Mac blocks the app** | Go to System Preferences → Security & Privacy → click "Open Anyway" |

---

## System Requirements

- macOS 10.15 (Catalina) or newer
- Python 3.9 or newer
- ~200 MB disk space (for Python + libraries)
- No internet required after initial setup

---

*For questions about the tool itself — what to enter, how to read the results — see the companion document: **User Guide.***
