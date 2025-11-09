require('dotenv').config();
const express = require('express');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const sessionRoutes = require('./routes/session');
const mlRoutes = require('./routes/ml');

const app = express();
const port = process.env.PORT || 4000;

const corsOptions = {
  origin: [
    'https://fire-auth-mcp.netlify.app', // Production frontend
    'http://localhost:5173',             // Local testing
  ],
  credentials: true,
};

app.use(cors(corsOptions));
app.use(express.json());
app.use(cookieParser());

app.use('/api', sessionRoutes);
app.use('/api', mlRoutes);

app.listen(port, () => {
  console.log(`✅ Server running on port ${port}`);
});
