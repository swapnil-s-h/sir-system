const multer = require('multer');
const path = require('path');
const express = require('express');
const cors = require('cors');
const pool = require('./db');

const app = express();
const PORT = process.env.PORT || 5000;

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname); // e.g., 1634567-boiler.jpg
  }
});
const upload = multer({ storage: storage });

// 2. Serve Static Files (Make images accessible via URL)
app.use('/uploads', express.static('uploads'));

// Middleware
app.use(cors());
app.use(express.json());

// Test Route
app.get('/', (req, res) => {
  res.send('Forbes Marshall SIR System API is running');
});

// API Route: Get All Checklist Templates (for the dropdown selection)
app.get('/api/templates', async (req, res) => {
  try {
    const allTemplates = await pool.query('SELECT * FROM checklist_templates');
    res.json(allTemplates.rows);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// API Route: Get Checklist Items for a Specific Template
app.get('/api/templates/:id/items', async (req, res) => {
  try {
    const { id } = req.params;
    const items = await pool.query(
      'SELECT * FROM checklist_items WHERE template_id = $1 ORDER BY id ASC',
      [id]
    );
    res.json(items.rows);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// API Route: Submit a New Inspection Report
app.post('/api/reports', async (req, res) => {
  const client = await pool.connect();
  try {
    const { inspector_id, template_id, location, inspection_date, items } = req.body;

    await client.query('BEGIN');

    const reportResult = await client.query(
      `INSERT INTO inspection_reports (inspector_id, template_id, location, inspection_date, status)
       VALUES ($1, $2, $3, $4, 'SUBMITTED') RETURNING id`,
      [inspector_id, template_id, location, inspection_date]
    );
    const reportId = reportResult.rows[0].id;

    for (const item of items) {
      await client.query(
        `INSERT INTO inspection_findings (report_id, checklist_item_id, status, observation_text, severity, evidence_url)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [reportId, item.checklist_item_id, item.status, item.observation, item.severity, item.evidenceUrl || null]
      );
    }

    await client.query('COMMIT');
    res.status(201).json({ message: 'Report submitted successfully', reportId });

  } catch (err) {
    await client.query('ROLLBACK');
    console.error(err.message);
    res.status(500).send('Server Error');
  } finally {
    client.release();
  }
});

// API Route: Get All Inspection Reports (For Dashboard)
app.get('/api/reports', async (req, res) => {
  try {
    const query = `
      SELECT 
        r.id, 
        r.inspection_date, 
        r.status, 
        r.location, 
        u.username as inspector_name, 
        t.title as template_title 
      FROM inspection_reports r
      JOIN users u ON r.inspector_id = u.id
      JOIN checklist_templates t ON r.template_id = t.id
      ORDER BY r.inspection_date DESC
    `;
    const result = await pool.query(query);
    res.json(result.rows);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// API Route: Get Single Report Details (Header + Findings + CAPA)
app.get('/api/reports/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // 1. Fetch Report Header
    const reportQuery = `
      SELECT r.*, u.username as inspector_name, t.title as template_title 
      FROM inspection_reports r
      JOIN users u ON r.inspector_id = u.id
      JOIN checklist_templates t ON r.template_id = t.id
      WHERE r.id = $1
    `;
    const reportResult = await pool.query(reportQuery, [id]);

    if (reportResult.rows.length === 0) {
      return res.status(404).json({ message: 'Report not found' });
    }

    // 2. Fetch Findings WITH CAPA info (Updated Query)
    const findingsQuery = `
      SELECT 
        f.id as finding_id, 
        f.status, 
        f.observation_text, 
        f.severity,
        f.evidence_url,
        i.item_text, 
        i.category,
        c.id as capa_id,
        c.action_description,
        c.status as capa_status,
        c.target_date,
        u.username as assigned_user
      FROM inspection_findings f
      JOIN checklist_items i ON f.checklist_item_id = i.id
      LEFT JOIN capa_actions c ON f.id = c.finding_id
      LEFT JOIN users u ON c.assigned_to = u.id
      WHERE f.report_id = $1
      ORDER BY i.id ASC
    `;
    const findingsResult = await pool.query(findingsQuery, [id]);

    res.json({
      report: reportResult.rows[0],
      findings: findingsResult.rows
    });

  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// API Route: Assign a CAPA to a Finding
app.post('/api/capa', async (req, res) => {
  try {
    const { finding_id, action_description, assigned_to, target_date } = req.body;
    
    const newCapa = await pool.query(
      `INSERT INTO capa_actions (finding_id, action_description, assigned_to, target_date)
       VALUES ($1, $2, $3, $4) RETURNING *`,
      [finding_id, action_description, assigned_to, target_date]
    );

    res.json(newCapa.rows[0]);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

app.post('/api/upload', upload.single('evidence'), (req, res) => {
  try {
    const fileUrl = `http://localhost:5000/uploads/${req.file.filename}`;
    res.json({ url: fileUrl });
  } catch (err) {
    console.error(err);
    res.status(500).send('File Upload Error');
  }
});

// API Route: Mark CAPA as Closed/Complete
app.patch('/api/capa/:id/close', async (req, res) => {
  try {
    const { id } = req.params;
    
    const result = await pool.query(
      `UPDATE capa_actions 
       SET status = 'CLOSED' 
       WHERE id = $1 
       RETURNING *`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'CAPA not found' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});