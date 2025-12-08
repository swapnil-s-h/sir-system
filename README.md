## 1. Install PostgreSQL
Install PostgreSQL locally (e.g., via pgAdmin or installer).
Then create a database:
```bash
forbes_sir_db
```
## 2. Create Tables
Run the following SQL script in the newly created database:
```bash
-- 1. Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) CHECK (role IN ('inspector', 'manager', 'admin')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Checklist Templates
CREATE TABLE checklist_templates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Checklist Items
CREATE TABLE checklist_items (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES checklist_templates(id),
    category VARCHAR(50),
    item_text TEXT NOT NULL,
    is_critical BOOLEAN DEFAULT FALSE
);

-- 4. Inspection Reports
CREATE TABLE inspection_reports (
    id SERIAL PRIMARY KEY,
    inspector_id INTEGER REFERENCES users(id),
    template_id INTEGER REFERENCES checklist_templates(id),
    location VARCHAR(100),
    scope TEXT,
    inspection_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'SUBMITTED', 'REVIEWED', 'CLOSED')),
    overall_evaluation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Inspection Findings
CREATE TABLE inspection_findings (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES inspection_reports(id),
    checklist_item_id INTEGER REFERENCES checklist_items(id),
    status VARCHAR(10) CHECK (status IN ('PASS', 'FAIL', 'NA')),
    observation_text TEXT,
    severity VARCHAR(10)
        CHECK (severity IN ('LOW', 'MINOR', 'MAJOR', 'CRITICAL')),
    evidence_url TEXT
);

-- 6. Corrective & Preventive Actions (CAPA)
CREATE TABLE capa_actions (
    id SERIAL PRIMARY KEY,
    finding_id INTEGER REFERENCES inspection_findings(id),
    action_description TEXT NOT NULL,
    assigned_to INTEGER REFERENCES users(id),
    target_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN'
        CHECK (status IN ('OPEN', 'IN_PROGRESS', 'CLOSED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
## 3. Insert Dummy Data
Run this script to insert sample users, templates, and checklist items:
```bash
-- Users
INSERT INTO users (username, email, role) VALUES 
('arjun_inspector', 'arjun.s@forbesmarshall.com', 'inspector'),
('priya_manager', 'priya.m@forbesmarshall.com', 'manager');

-- Checklist Templates
INSERT INTO checklist_templates (title, description) VALUES 
('Industrial Boiler Inspection (Annual)', 'Comprehensive check based on ASME and Forbes Marshall maintenance schedules.'),
('Control Valve Preventive Maintenance', 'Standard check for wear, calibration, and API 598 leakage standards.');

-- Boiler Checklist Items – Template ID 1
INSERT INTO checklist_items (template_id, category, item_text, is_critical) VALUES 
(1, 'Safety Devices', 'Verify Safety Relief Valve (SRV) pop pressure is within set limits.', TRUE),
(1, 'Safety Devices', 'Test Low-Water Cutoff (LWCO) mechanism for immediate boiler trip.', TRUE),
(1, 'Safety Devices', 'Check flame scanner/sensor for proper signal detection.', TRUE),
(1, 'Internal Condition', 'Inspect steam drum internals for scaling, pitting, or corrosion.', FALSE),
(1, 'Internal Condition', 'Check water wall tubes for signs of overheating or blistering.', FALSE),
(1, 'Internal Condition', 'Inspect refractory lining for cracks or spalling.', FALSE),
(1, 'External Condition', 'Check insulation and cladding for hot spots or damage.', FALSE),
(1, 'External Condition', 'Inspect fuel piping for leaks (gas/oil line integrity).', TRUE),
(1, 'Water Chemistry', 'Verify TDS (Total Dissolved Solids) levels are within operational limits.', FALSE),
(1, 'Water Chemistry', 'Check pH level of feedwater to prevent corrosion.', FALSE);

-- Control Valve Checklist Items – Template ID 2
INSERT INTO checklist_items (template_id, category, item_text, is_critical) VALUES 
(2, 'Calibration', 'Verify valve stroke travel (0% to 100%) matches positioner feedback.', TRUE),
(2, 'Calibration', 'Check for hysteresis or stick-slip movement during operation.', FALSE),
(2, 'Physical Inspection', 'Inspect actuator diaphragm for signs of aging or air leaks.', TRUE),
(2, 'Physical Inspection', 'Check stem packing for leakage; tighten gland nuts if necessary.', FALSE),
(2, 'Physical Inspection', 'Inspect valve body and bonnet for external corrosion.', FALSE),
(2, 'Leakage Testing', 'Perform Seat Leakage Test (Class IV/V/VI shutoff capability).', TRUE),
(2, 'Leakage Testing', 'Verify air supply filter regulator is clean and stable.', FALSE);
```
## 4. Configure Backend Connection (server/db.js)
Edit the placeholders with your PostgreSQL credentials:
```bash
const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'forbes_sir_db',
  password: process.env.DB_PASSWORD || 'your_password',
  port: process.env.DB_PORT || 5432,
});

module.exports = pool;
```

## 5. Run the Backend Server
Inside the /server folder:
```bash
npm install
npm start
```

## 6. Run the AI Service
Open a new terminal and navigate to the AI service directory:
```bash
cd ai_service
```

Create a virtual environment:
```bash
# On Windows
python -m venv venv

# On macOS/Linux
python3 -m venv venv
```

Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

Run the AI service:
```bash
python app.py
```

## 7. Run the React Client
Inside the /client folder:
```bash
npm install
npm start
```
The app will open at:
```bash
http://localhost:3000
```