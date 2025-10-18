# 📦 Project Setup

---

# 🧩 1. Install Homebrew (Mac Only)

> Skip this step if you're on Windows.

Homebrew is a package manager for macOS.  
You’ll use it to easily install Git, Python, Docker, etc.

**Install Homebrew:**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Verify Homebrew:

bash
Copy code
brew --version
If you see a version number, you're good to go.

🧩 2. Install and Configure Git
Install Git
MacOS (using Homebrew)

bash
Copy code
brew install git
Windows

Download and install Git for Windows.
Accept the default options during installation.

Verify Git:

bash
Copy code
git --version
Configure Git Globals
Set your name and email so Git tracks your commits properly:

bash
Copy code
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
Confirm the settings:

bash
Copy code
git config --list
Generate SSH Keys and Connect to GitHub
Only do this once per machine.

Generate a new SSH key:

bash
Copy code
ssh-keygen -t ed25519 -C "your_email@example.com"
(Press Enter at all prompts.)

Start the SSH agent:

bash
Copy code
eval "$(ssh-agent -s)"
Add the SSH private key to the agent:

bash
Copy code
ssh-add ~/.ssh/id_ed25519
Copy your SSH public key:

Mac/Linux:

bash
Copy code
cat ~/.ssh/id_ed25519.pub | pbcopy
Windows (Git Bash):

bash
Copy code
cat ~/.ssh/id_ed25519.pub | clip
Add the key to your GitHub account:

Go to GitHub SSH Settings

Click New SSH Key, paste the key, save.

Test the connection:

bash
Copy code
ssh -T git@github.com
You should see a success message.

🧩 3. Clone the Repository
Now you can safely clone the course project:

bash
Copy code
git clone <repository-url>
cd <repository-directory>
🛠️ 4. Install Python 3.10+
Install Python
MacOS (Homebrew)

bash
Copy code
brew install python
Windows

Download and install Python for Windows.
✅ Make sure you check the box Add Python to PATH during setup.

Verify Python:

bash
Copy code
python3 --version
or

bash
Copy code
python --version
Create and Activate a Virtual Environment
(Optional but recommended)

bash
Copy code
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
Install Required Packages
bash
Copy code
pip install -r requirements.txt
🐳 5. (Optional) Docker Setup
Skip if Docker isn't used in this module.

Install Docker
Install Docker Desktop for Mac

Install Docker Desktop for Windows

Build Docker Image
bash
Copy code
docker build -t <image-name> .
Run Docker Container
bash
Copy code
docker run -it --rm <image-name>
🚀 6. Running the Project
Without Docker:

bash
Copy code
python main.py
(or update this if the main script is different.)

With Docker:

bash
Copy code
docker run -it --rm <image-name>
🎨 6.1 Enabling Color Output in Calculator REPL
You can enable colorized output in the calculator’s command-line interface using the colorama package.

Follow these steps to install and configure it in your virtual environment (.venv):

bash
Copy code
(.venv) user@Mazz-2023:~/projects/assignment6$ pip install colorama
Collecting colorama
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Installing collected packages: colorama
Successfully installed colorama-0.4.6
🧭 Enable Color Mode
Add the following line to your ~/.bashrc file so color mode is automatically enabled each time you open a terminal:

bash
Copy code
echo 'export CALCULATOR_COLOR=1' >> ~/.bashrc
Reload your terminal or source the file:

bash
Copy code
source ~/.bashrc
▶️ Run the Calculator
Start the calculator from your project root:

bash
Copy code
(.venv) user@Mazz-2023:~/projects/assignment6$ python3 main.py
Calculator started. Type 'help' for commands.
Enter command: add

Enter numbers (or 'cancel' to abort):
First number: 2
Second number: 2

Result: 4
Enter command: 4
Unknown command: '4'. Type 'help' for available commands.
Enter command: history

Calculation History:
1. Addition(4, 5) = 9
2. Addition(2, 2) = 4
3. Addition(1, 1) = 2
4. Addition(1, 1) = 2
5. Addition(2, 2) = 4
Enter command: load
History loaded successfully
Enter command: save
History saved successfully
Enter command: help

Available commands:
  add, subtract, multiply, divide, power, root, modulus, intdiv, percentage, absdiff
  history  - Show calculation history
  clear    - Clear calculation history
  undo     - Undo the last calculation
  redo     - Redo the last undone calculation
  save     - Save calculation history to file
  load     - Load calculation history from file
  exit     - Exit the calculator
Enter command: exit
History saved successfully.
Goodbye!
💡 Notes
Color output only appears in a real terminal (TTY) — not in IDE “Debug Consoles.”

To force color output even when not using a TTY, set:

bash
Copy code
export CALCULATOR_COLOR_FORCE=1
Ensure colorama is installed in the same .venv you’re running the calculator from.

📝 7. Submission Instructions
After finishing your work:

bash
Copy code
git add .
git commit -m "Complete Module X"
git push origin main
Then submit the GitHub repository link as instructed.

🔥 Useful Commands Cheat Sheet
Action	Command
Install Homebrew (Mac)	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Install Git	brew install git or Git for Windows installer
Configure Git Global Username	git config --global user.name "Your Name"
Configure Git Global Email	git config --global user.email "you@example.com"
Clone Repository	git clone <repo-url>
Create Virtual Environment	python3 -m venv venv
Activate Virtual Environment	source venv/bin/activate / venv\Scripts\activate.bat
Install Python Packages	pip install -r requirements.txt
Build Docker Image	docker build -t <image-name> .
Run Docker Container	docker run -it --rm <image-name>
Push Code to GitHub	git add . && git commit -m "message" && git push

📋 Notes
Install Homebrew first on Mac.

Install and configure Git and SSH before cloning.

Use Python 3.10+ and virtual environments for Python projects.

Docker is optional depending on the project.

📎 Quick Links
Homebrew

Git Downloads

Python Downloads

Docker Desktop

GitHub SSH Setup Guide