import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

const API =
  import.meta.env.VITE_API_URL ||
  '/api';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App API={API} />
  </React.StrictMode>
);
