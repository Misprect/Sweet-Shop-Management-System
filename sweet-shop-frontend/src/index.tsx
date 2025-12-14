// src/index.tsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';

// If you are using Bootstrap (as suggested by your class names like 'container-fluid', 
// you should also include the CSS here if you haven't already in App.tsx or index.html)
// import 'bootstrap/dist/css/bootstrap.min.css'; 

// 1. Find the root DOM element
const rootElement = document.getElementById('root'); 

if (rootElement) {
    // 2. Create the React 18 root
    ReactDOM.createRoot(rootElement).render(
        <React.StrictMode>
            {/* 3. Render the main application component */}
            <App />
        </React.StrictMode>
    );
} else {
    // This should ideally never run if index.html is correct
    console.error("Failed to find the root element in the document.");
}