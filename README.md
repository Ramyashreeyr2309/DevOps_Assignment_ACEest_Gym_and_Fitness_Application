ACEest Functional Fitness Web App
This is a Flask-based web application designed to manage fitness programs, including tailored workout and diet plans. It features a dynamic dashboard where users can view specific program details and client data pulled from an integrated SQLite database.

 FeaturesProgram Selection: 
 Toggle between "Fat Loss", "Muscle Gain", and "Beginner" programs.
 
 Dynamic Data: Fetches workout routines, nutritional plans, and UI color schemes via a JSON API.Database Integration: Connects to a SQLite backend to manage client memberships and progress.Automated Testing: Includes a comprehensive suite for validating API endpoints and data integrity.
 
 Project StructurePlaintext.
├── app/
│   ├── app.py              # Main Flask application 
│   ├── aceest_fitness.db   # SQLite database file 
│   ├── requirements.txt    # Project dependencies 
│   └── templates/
│       └── index.html      # Main dashboard frontend 
├── test_app.py             # Pytest test suite 
└── .github/workflows/      # CI/CD pipeline configuration 

Installation & Setup
1. PrerequisitesEnsure you have Python 3.10 or higher installed.
2. Virtual EnvironmentCreate and activate a virtual environment to manage dependencies:Bashpython -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
3. Install DependenciesInstall the required packages using the requirements.txt file located in the app/ directory:Bashpip install -r app/requirements.txt
Running the ApplicationTo start the local development server, 
run:Bashpython app/app.py
The application will be available at http://127.0.0.1:5000/. 

TestingThe project uses pytest for unit testing. To run the tests, ensure your PYTHONPATH is set to the app directory:Windows (PowerShell):PowerShell$env:PYTHONPATH = ".\app"

pytest test_app.py


macOS/Linux:Bashexport PYTHONPATH=$PYTHONPATH:$(pwd)/app

pytest test_app.py

CI/CD Integration
This repository is configured with GitHub Actions to automatically validate code quality. The workflow triggers on any Pull Request targeting the release branch. 
It performs the following steps:

Sets up a Python 3.10 environment.
Installs dependencies from app/requirements.txt.
Executes pytest to ensure all functional tests pass before merging.

APP_V_1_1_0 app

New Endpoint: 
A new POST route, /save_client, was added in version 1.1 to handle saving or updating client information in the database. It includes logic to handle database conflicts using ON CONFLICT(name) DO UPDATE

APP_V_1_1_2
Added Client List, Progress Report in website

APP_V_2_0_1
Introduces automatic calorie calculation logic

APP_V_2_1_2
Added new featues to code

APP_V2.2.1
Added a new GET route, /get_progress, allowing the frontend to fetch and display the history of a client's weekly adherence logs.

APP_V2.2.4
Transition from a simple information-display tool to a data-driven tracking system with automated calculations and API-oriented architecture.

APP_V3.0.1
comprehensive fitness management system with historical data logging.

APP_V3.2.1
data-tracking tool to a secure, "premium" fitness management system. The focus shifted heavily toward Security (Authentication) and Client Deliverables (PDF Reporting).

APP_V3.3.1
Added Features and final output


Running Pytest manually

To execute pytest manually for your Aceest Gym and Fitness Application, you need to ensure your environment is set up correctly so that the test script can find your application code.

Follow these steps in your terminal (Command Prompt or PowerShell):

1. Activate your Virtual Environment
Before running any commands, you must be inside the virtual environment where your dependencies (Flask, FPDF, pytest, etc.) are installed.

PowerShell
# Navigate to your project root first
cd C:\Users\Ramya_Shashank\DevOps_Assignment_ACEest_Gym_and_Fitness_Application

# Activate the venv
.\venv\Scripts\activate
2. Set the Python Path
Since your project structure puts the code inside an app folder, pytest needs to know where to look for app.py when it sees from app import... in your test file.

PowerShell
# Windows (cmd)
set PYTHONPATH=%CD%\app

# Windows (PowerShell)
$env:PYTHONPATH = "$pwd\app"
3. Run the Tests
You can run all tests, a specific file, or even a specific test case.

Run everything:

PowerShell
python -m pytest
Run just the specific test file:

PowerShell
python -m pytest app/test_app.py
Run and see the output of print statements (Verbose mode):

PowerShell
python -m pytest -v -s app/test_app.py


Jenkins and Github Actions Overview
For a high-level overview, both Jenkins and GitHub Actions serve the same goal: Automating the lifecycle of your ACEest Fitness App. However, they differ in where they run and how they are configured.

1. GitHub Actions (The "Cloud-Native" Workflow)
GitHub Actions is integrated directly into your repository. It uses Event-Triggers (like a git push) to start a job on GitHub's hosted servers.

Workflow Steps:
Trigger: You push code to the main branch.

Environment Setup: GitHub spins up a temporary Ubuntu or Windows "Runner."

Install Dependencies: It reads your requirements.txt and installs Flask, FPDF, etc.

Linting/Static Analysis: It checks your Python code for syntax errors.

Run Pytest: It executes your test_app.py. If tests fail, the build stops, and you see a red "X" on your commit.

Deploy (Optional): If tests pass, it can automatically push the app to a cloud provider (like Heroku or AWS).

2. Jenkins (The "Self-Hosted" Workflow)
Jenkins is an automation server usually installed on your local machine or a private server. It is highly customizable via the Jenkinsfile.

Workflow Steps:
Poll SCM / Webhook: Jenkins detects a change in your local Git folder or GitHub repo.

Build Stage: Jenkins creates a Virtual Environment (venv) on your computer.

Test Stage: It sets the PYTHONPATH and runs pytest. It often generates a JUnit XML report to show a graph of test results.

Artifact Archiving: Jenkins can "package" your app.py and database into a ZIP file or a Docker image for safekeeping.

Post-Build: It sends an email or Slack notification if the ACEest app build failed.