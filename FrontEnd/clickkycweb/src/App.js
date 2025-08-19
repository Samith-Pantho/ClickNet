import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import MasterPage from './pages/MasterPage';
import Callback from './pages/CallbackPage';
import './App.css';

function App() {
  return (
    <Router>
        <AuthProvider>
          <div className="app-container">
            <Header />
            
            <main className="main-content">
              <Routes>
                <Route path="/" element={<MasterPage />} />
                <Route path="/callback" element={<Callback />} />
              </Routes>
            </main>
            
            <Footer />
          </div>
        </AuthProvider>
    </Router>
  );
}

export default App;