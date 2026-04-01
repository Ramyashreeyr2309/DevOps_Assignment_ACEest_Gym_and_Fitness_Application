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