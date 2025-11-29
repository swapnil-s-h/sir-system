const jwt = require('jsonwebtoken');

// Use a strong secret key (In production, put this in .env file)
const JWT_SECRET = 'super_secret_key_for_forbes_marshall_project'; 

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Format: "Bearer <TOKEN>"

  if (!token) return res.status(401).json({ message: 'Access Denied: No Token Provided' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ message: 'Invalid Token' });
    
    // Attach the user info (id, role) to the request object
    req.user = user;
    next(); // Pass control to the next function (the actual API)
  });
};

module.exports = { authenticateToken, JWT_SECRET };