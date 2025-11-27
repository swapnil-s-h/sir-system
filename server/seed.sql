-- 1. Insert Users (Mock Data)
INSERT INTO users (username, email, role) VALUES 
('arjun_inspector', 'arjun.s@forbesmarshall.com', 'inspector'),
('priya_manager', 'priya.m@forbesmarshall.com', 'manager');

-- 2. Insert Checklist Templates
INSERT INTO checklist_templates (title, description) VALUES 
('Industrial Boiler Inspection (Annual)', 'Comprehensive check based on ASME and Forbes Marshall maintenance schedules.'),
('Control Valve Preventive Maintenance', 'Standard check for wear, calibration, and API 598 leakage standards.');

-- 3. Insert Checklist Items for BOILERS (Template ID 1)
-- Categories derived from ASME Power Boiler Inspection guidelines
INSERT INTO checklist_items (template_id, category, item_text, is_critical) VALUES 
-- Safety Devices (Critical)
(1, 'Safety Devices', 'Verify Safety Relief Valve (SRV) pop pressure is within set limits.', TRUE),
(1, 'Safety Devices', 'Test Low-Water Cutoff (LWCO) mechanism for immediate boiler trip.', TRUE),
(1, 'Safety Devices', 'Check flame scanner/sensor for proper signal detection.', TRUE),

-- Internal Condition (Tubes/Drums)
(1, 'Internal Condition', 'Inspect steam drum internals for scaling, pitting, or corrosion.', FALSE),
(1, 'Internal Condition', 'Check water wall tubes for signs of overheating or blistering.', FALSE),
(1, 'Internal Condition', 'Inspect refractory lining for cracks or spalling.', FALSE),

-- External & Structural
(1, 'External Condition', 'Check insulation and cladding for hot spots or damage.', FALSE),
(1, 'External Condition', 'Inspect fuel piping for leaks (gas/oil line integrity).', TRUE),

-- Water Quality
(1, 'Water Chemistry', 'Verify TDS (Total Dissolved Solids) levels are within operational limits.', FALSE),
(1, 'Water Chemistry', 'Check pH level of feedwater to prevent corrosion.', FALSE);

-- 4. Insert Checklist Items for CONTROL VALVES (Template ID 2)
-- Categories derived from API 598 Valve Inspection & Testing standards
INSERT INTO checklist_items (template_id, category, item_text, is_critical) VALUES 
-- Calibration & Function
(2, 'Calibration', 'Verify valve stroke travel (0% to 100%) matches positioner feedback.', TRUE),
(2, 'Calibration', 'Check for hysteresis or "stick-slip" movement during operation.', FALSE),

-- Physical Integrity
(2, 'Physical Inspection', 'Inspect actuator diaphragm for signs of aging, cracking, or air leaks.', TRUE),
(2, 'Physical Inspection', 'Check stem packing for leakage; tighten gland nuts if necessary.', FALSE),
(2, 'Physical Inspection', 'Inspect valve body and bonnet for external corrosion or erosion.', FALSE),

-- Performance Testing (API 598)
(2, 'Leakage Testing', 'Perform Seat Leakage Test (Class IV/V/VI shutoff capability).', TRUE),
(2, 'Leakage Testing', 'Verify air supply filter regulator is clean and pressure is stable.', FALSE);