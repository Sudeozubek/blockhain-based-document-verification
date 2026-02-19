<h1 align="center">Blockchain-Based Document Integrity Verification System</h1>

<hr>

[Project_Plan_Final.xlsx](https://github.com/user-attachments/files/25420662/Project_Plan_Final.xlsx)

Group members
<li> ⁠Özge Zelal Küçük — Project Manager
<li> ⁠Kevser Agdas — System Analyst
<li> ⁠Muhammed Dönmez — Backend Developer
<li> ⁠Sude Özübek — Frontend Developer
<li> ⁠Yağmur Saraçoğlu — QA & DevOpos

Jira Board: 
https://stu-team-xpgexxr4.atlassian.net/jira/software/projects/SCRUM/boards/1


<h2>1. Project Description</h2>

<p>
This project aims to design and implement a web-based document integrity verification system 
using cryptographic hashing (SHA-256) and a simulated blockchain structure.
</p>

<p>
The system allows users to upload PDF contracts, generates a secure hash of the document, 
and stores the hash in a blockchain-like data structure. If the document is modified at any 
time in the future, the system detects the change by comparing hashes and validating the chain.
</p>

<p>
The primary objective of this project is to demonstrate data integrity verification principles 
within a structured Software Development Life Cycle (SDLC).
</p>

<hr>

<h2>2. Project Objectives</h2>

<ul>
<li>Implement SHA-256 hashing for document fingerprinting</li>
<li>Simulate a blockchain structure for immutable record storage</li>
<li>Design a modular backend architecture using Flask</li>
<li>Integrate authentication and role-based access control</li>
<li>Apply Agile (Scrum-based) SDLC methodology</li>
<li>Implement unit and integration testing</li>
<li>Document system architecture and testing processes</li>
</ul>

<hr>

<h2>3. System Architecture</h2>

<p>The system follows a modular Flask architecture using the App Factory Pattern.</p>

<p><strong>Architecture Layers:</strong></p>

<ul>
<li>Presentation Layer (HTML, CSS, JavaScript, Bootstrap)</li>
<li>API Layer (Flask Routes)</li>
<li>Business Logic Layer (Hashing & Blockchain Services)</li>
<li>Data Layer (SQLite with SQLAlchemy ORM)</li>
<li>Testing Layer (pytest)</li>
</ul>

<hr>

<h2> UML Diagram </h2>

<img width="1302" height="796" alt="image" src="https://github.com/user-attachments/assets/31a3923f-b717-4186-9968-045585393b2e" />


<h2>4. Technology Stack</h2>

<h3>Backend</h3>
<ul>
<li>Python 3.11</li>
<li>Flask 3.x</li>
<li>SQLAlchemy</li>
<li>Flask-JWT-Extended</li>
</ul>

<h3>Frontend</h3>
<ul>
<li>HTML5</li>
<li>CSS3</li>
<li>Bootstrap 5</li>
<li>JavaScript (Fetch API)</li>
</ul>

<h3>Database</h3>
<ul>
<li>SQLite 3</li>
</ul>

<h3>Testing</h3>
<ul>
<li>pytest</li>
<li>pytest-cov</li>
</ul>

<hr>

<h2>5. Project Structure</h2>

<pre>
blockchain-doc-verify/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   └── extensions.py
│
├── database/
├── tests/
├── docs/
├── uploads/
├── migrations/
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
</pre>

<hr>

<h2>6. Core Functional Features</h2>

<ul>
<li>User registration and login (JWT-based authentication)</li>
<li>Upload PDF contracts</li>
<li>Generate SHA-256 hash</li>
<li>Store hash in blockchain structure</li>
<li>Verify document integrity</li>
<li>Blockchain validation mechanism</li>
<li>Audit logging</li>
<li>Unit and integration testing</li>
</ul>

<hr>

<h2>7. SDLC Model</h2>

<p>This project follows an Agile (Scrum-based) Software Development Life Cycle.</p>

<ul>
<li>Requirement Analysis</li>
<li>Backlog Creation</li>
<li>Sprint Planning</li>
<li>Iterative Development</li>
<li>Continuous Testing</li>
<li>Sprint Review</li>
<li>Final Deployment</li>
</ul>

<p>
Risk management, Work Breakdown Structure (WBS), and UML modeling were also 
conducted as part of the project documentation.
</p>

<hr>

<h2>8. Installation & Execution</h2>

<h3>Clone Repository</h3>

<pre>
git clone https://github.com/your-username/blockchain-doc-verify.git
cd blockchain-doc-verify
</pre>

<h3>Create Virtual Environment</h3>

<pre>
python -m venv venv
</pre>

<h3>Install Dependencies</h3>

<pre>
pip install -r requirements.txt
</pre>

<h3>Run Database Migration</h3>

<pre>
flask db upgrade
</pre>

<h3>Start Application</h3>

<pre>
python run.py
</pre>

<hr>

<h2>9. Testing</h2>

<pre>
pytest
</pre>

<p>For coverage report:</p>

<pre>
pytest --cov=app
</pre>

<hr>

<h2>10. Success Criteria</h2>

<ul>
<li>Uploaded documents can be verified without false positives</li>
<li>Modified documents are detected accurately</li>
<li>Blockchain validation works correctly</li>
<li>All core features pass unit tests</li>
<li>Project is delivered according to Agile planning</li>
</ul>

<hr>

<p align="center">
Developed as part of an academic Project Management course.
</p>
