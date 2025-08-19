import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaRobot, FaTimes, FaPaperPlane, FaPlus, FaCircle } from 'react-icons/fa';
import { chatWithAI } from '../../services/bankingService';
import { WS_BASE_URL } from '../../utils/constants';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: 'Hi, I am ClickNet Bot. How may I help you?', isBot: true }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [socket, setSocket] = useState(null);
  const [socketId, setSocketId] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const suggestionsRef = useRef(null);
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    'How do I transfer money?',
    'How to reset my password?',
    'Where can I find my account statement?',
    'How do I check my transaction history?',
    'Where can I report a complaint?',
  ];

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeChat = async () => {
    if (isOpen) return;
    if (!socket && !socketId) {
      try {
        setIsLoading(true);
        setConnectionStatus('connecting');
        const response = await chatWithAI({ message: '' });
        
        if (response.data.Status === 'OK') {
          const wsId = response.data.Result;
          setSocketId(wsId);
          
          const newSocket = new WebSocket(
            `${window.location.protocol === "https:" ? "wss" : "ws"}://${WS_BASE_URL}/initialize/${wsId}`
          );
          
          newSocket.onopen = () => {
            setConnectionStatus('connected');
            setIsLoading(false);
          };

          newSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.ROLE === 'OPENAI') {
              setMessages(prev => [...prev, { text: data.MESSAGE, isBot: true }]);
            }
          };
          
          newSocket.onclose = () => {
            setConnectionStatus('disconnected');
            setSocket(null);
            setSocketId(null);
          };

          newSocket.onerror = () => {
            setConnectionStatus('disconnected');
          };
          
          setSocket(newSocket);
        }
      } catch (error) {
        setConnectionStatus('disconnected');
        setMessages(prev => [...prev, { 
          text: 'Failed to initialize chat. Please try again.', 
          isBot: true 
        }]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const toggleChat = () => {
    initializeChat();
    setIsOpen(prev => !prev);
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    const userMessage = { text: inputMessage, isBot: false };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      await chatWithAI(inputMessage);
      console.log(socket);

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(data);
        if (data.ROLE === 'OPENAI') {
          setMessages(prev => [...prev, { text: data.MESSAGE, isBot: true }]);
        }
      };
      
      socket.onclose = () => {
        setConnectionStatus('disconnected');
        setSocket(null);
        setSocketId(null);
      };

      socket.onerror = () => {
        setConnectionStatus('disconnected');
      };
      
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: 'An error occurred. Please try again.', 
        isBot: true 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question) => {
    setInputMessage(question);
    setShowSuggestions(false);
    handleSendMessage();
  };

  return (
    <>
      <motion.button
        className="chatbot-toggle"
        onClick={toggleChat}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        {isOpen ? <FaTimes /> : <FaRobot />}
      </motion.button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="chatbot-container"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            <div className="chatbot-header">
              <h3>ClickNet Assistant</h3>
              <div className={`connection-status ${connectionStatus}`}>
                <FaCircle className="status-icon" />
                <span>{
                  connectionStatus === 'connected' ? 'Live' : 
                  connectionStatus === 'connecting' ? 'Connecting...' : 'Offline'
                }</span>
              </div>
            </div>
            
            <div className="chatbot-messages">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.isBot ? 'bot' : 'user'}`}>
                  {msg.text}
                  <div className="message-time">
                    {new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="message bot">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <div className="message-time">
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            
            <div className="chatbot-input-container">
              <div className="chatbot-input">
                <button 
                  className="suggestions-toggle"
                  onClick={() => setShowSuggestions(!showSuggestions)}
                >
                  <FaPlus />
                </button>
                
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Type your message..."
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                
                <button 
                  onClick={handleSendMessage}
                  disabled={isLoading}
                  className='cursor-pointer'
                >
                  <FaPaperPlane />
                </button>
              </div>
              
              <AnimatePresence>
                {showSuggestions && (
                  <motion.div 
                    className="suggested-questions-popup"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    ref={suggestionsRef}
                  >
                    {suggestedQuestions.map((question, index) => (
                      <div
                        key={index}
                        className="suggestion-item"
                        onClick={() => handleSuggestedQuestion(question)}
                      >
                        {question}
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatBot;