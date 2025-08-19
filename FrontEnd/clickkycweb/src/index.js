import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { ConfigProvider } from './contexts/ConfigContext';
import './index.css';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <ConfigProvider>
      <App />
    </ConfigProvider>
  </React.StrictMode>
);