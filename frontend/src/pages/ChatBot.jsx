// import React, { useState, useEffect, useRef } from 'react';
// import "../assets/chat.css";

// function ChatBot() {
//   const [messages, setMessages] = useState([
//     { text: "Hello! I'm your AI Health Assistant. How can I help you today?", sender: 'ai' },
//   ]);
//   const [userInput, setUserInput] = useState('');
//   const [sessionId, setSessionId] = useState(null);
//   const [selectedImage, setSelectedImage] = useState(null);
//   const [isLoading, setIsLoading] = useState(false);
//   const messageContainerRef = useRef(null);
  
//   useEffect(() => {
//     setSessionId(Math.random().toString(36).substring(7));
    
//     if (messageContainerRef.current) {  
//       messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
//     }
//   }, [messages]);

//   async function sendMessage() {
//     if (!userInput.trim() && !selectedImage) return;

//     const newUserMessage = { text: userInput, sender: 'user', image: selectedImage };
//     setMessages((prevMessages) => [...prevMessages, newUserMessage]);

//     setUserInput('');
//     setSelectedImage(null);
//     setIsLoading(true);

//     try {
//       const requestBody = {
//         input: userInput,
//         session_id: sessionId,
//         image: selectedImage ? selectedImage.split(',')[1] : null,
//       };

//       const response = await fetch('http://127.0.0.1:5000/chat', {
//         method: 'POST',
//         headers: { 
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(requestBody),
//       });

//       const data = await response.json();

//       if (response.ok) {
//         const newAIMessage = { text: data.response, sender: 'ai' };
//         setMessages((prevMessages) => [...prevMessages, newAIMessage]);
//       } else {
//         console.error('Error:', data.error);
//         const errorMessage = { 
//           text: data.error || "Sorry, I'm having trouble connecting to the server. Please try again.", 
//           sender: 'ai' 
//         };
//         setMessages((prevMessages) => [...prevMessages, errorMessage]);
//       }
//     } catch (error) {
//       console.error('Error connecting to server:', error);
//       const errorMessage = { 
//         text: "Sorry, I'm having trouble connecting to the server. Please try again.", 
//         sender: 'ai' 
//       };
//       setMessages((prevMessages) => [...prevMessages, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   }

//   const handleImageUpload = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       if (file.size > 5 * 1024 * 1024) {
//         alert('Please select an image smaller than 5MB');
//         return;
//       }
//       const reader = new FileReader();
//       reader.onloadend = () => {
//         setSelectedImage(reader.result);
//       };
//       reader.readAsDataURL(file);
//     }
//   };

//   return (
//     <div className="chat-container" style={{
//       maxWidth: '1200px',
//       margin: '0 auto',
//       padding: '20px',
//       height: '100vh',
//       display: 'flex',
//       flexDirection: 'column'
//     }}>
//       <main className="main" style={{flex: 1}}>
//         <div className="card" style={{
//           backgroundColor: '#fff',
//           borderRadius: '20px',
//           boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
//           height: '100%',
//           display: 'flex',
//           flexDirection: 'column'
//         }}>
//           <div className="card-header" style={{
//             padding: '25px',
//             borderBottom: '2px solid #f0f0f0',
//             textAlign: 'center',
//             backgroundColor: '#f8f9fa',
//             borderRadius: '20px 20px 0 0'
//           }}>
//             <h1 style={{
//               fontSize: '2rem',
//               color: '#2c3e50',
//               marginBottom: '10px'
//             }}><span className="icon">🏥</span> AI Health Assistant</h1>
//             <p style={{color: '#666', fontSize: '1.1rem'}}>Your personal guide to natural health and wellness</p>
//           </div>
          
//           <div className="card-content" style={{
//             flex: 1,
//             display: 'flex',
//             flexDirection: 'column',
//             padding: '20px'
//           }}>
//             <div className="message-container" ref={messageContainerRef} style={{
//               flex: 1,
//               overflowY: 'auto',
//               padding: '20px',
//               gap: '20px',
//               display: 'flex',
//               flexDirection: 'column'
//             }}>
//               {messages.map((message, index) => (
//                 <div key={index} className={`message ${message.sender}`} style={{
//                   maxWidth: '80%',
//                   alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
//                   backgroundColor: message.sender === 'user' ? '#007bff' : '#f8f9fa',
//                   color: message.sender === 'user' ? '#fff' : '#333',
//                   padding: '15px 20px',
//                   borderRadius: '15px',
//                   boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
//                 }}>
//                   <div className="message-content">
//                     {message.image && (
//                       <img src={message.image} alt="User uploaded" style={{
//                         maxWidth: '300px',
//                         borderRadius: '10px',
//                         marginBottom: '10px'
//                       }} />
//                     )}
//                     <p style={{margin: 0, lineHeight: '1.5'}}>{message.text}</p>
//                   </div>
//                   <span style={{
//                     fontSize: '0.8rem',
//                     opacity: 0.7,
//                     marginTop: '5px',
//                     display: 'block'
//                   }}>
//                     {new Date().toLocaleTimeString()}
//                   </span>
//                 </div>
//               ))}
//               {isLoading && (
//                 <div className="typing-indicator" style={{
//                   padding: '15px',
//                   display: 'flex',
//                   gap: '5px',
//                   justifyContent: 'center'
//                 }}>
//                   <span style={{
//                     width: '8px',
//                     height: '8px',
//                     backgroundColor: '#007bff',
//                     borderRadius: '50%',
//                     animation: 'bounce 1s infinite'
//                   }}></span>
//                   <span style={{
//                     width: '8px',
//                     height: '8px',
//                     backgroundColor: '#007bff',
//                     borderRadius: '50%',
//                     animation: 'bounce 1s infinite 0.2s'
//                   }}></span>
//                   <span style={{
//                     width: '8px',
//                     height: '8px',
//                     backgroundColor: '#007bff',
//                     borderRadius: '50%',
//                     animation: 'bounce 1s infinite 0.4s'
//                   }}></span>
//                 </div>
//               )}
//             </div>
            
//             <div className="input-container" style={{
//               display: 'flex',
//               gap: '10px',
//               padding: '20px',
//               borderTop: '2px solid #f0f0f0',
//               alignItems: 'center'
//             }}>
//               <input
//                 type="file"
//                 accept="image/*"
//                 onChange={handleImageUpload}
//                 style={{ display: 'none' }}
//                 id="image-upload"
//               />
//               <label htmlFor="image-upload" style={{
//                 cursor: 'pointer',
//                 fontSize: '1.5rem',
//                 padding: '10px',
//                 borderRadius: '50%',
//                 backgroundColor: '#f8f9fa',
//                 transition: 'background-color 0.2s'
//               }}>
//                 📷
//               </label>
              
//               {selectedImage && (
//                 <div style={{
//                   position: 'relative',
//                   width: '60px',
//                   height: '60px'
//                 }}>
//                   <img src={selectedImage} alt="Preview" style={{
//                     width: '100%',
//                     height: '100%',
//                     objectFit: 'cover',
//                     borderRadius: '8px'
//                   }} />
//                   <button onClick={() => setSelectedImage(null)} style={{
//                     position: 'absolute',
//                     top: -8,
//                     right: -8,
//                     backgroundColor: '#ff4444',
//                     color: '#fff',
//                     border: 'none',
//                     borderRadius: '50%',
//                     width: '20px',
//                     height: '20px',
//                     cursor: 'pointer'
//                   }}>×</button>
//                 </div>
//               )}
              
//               <input
//                 type="text"
//                 className="message-input"
//                 placeholder="Type your health-related question..."
//                 value={userInput}
//                 onChange={(e) => setUserInput(e.target.value)}
//                 onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
//                 style={{
//                   flex: 1,
//                   padding: '15px',
//                   borderRadius: '25px',
//                   border: '2px solid #e0e0e0',
//                   fontSize: '1rem',
//                   transition: 'border-color 0.2s',
//                   outline: 'none'
//                 }}
//               />
              
//               <button 
//                 onClick={sendMessage}
//                 disabled={isLoading}
//                 style={{
//                   backgroundColor: '#007bff',
//                   color: '#fff',
//                   border: 'none',
//                   padding: '15px 30px',
//                   borderRadius: '25px',
//                   fontSize: '1rem',
//                   cursor: 'pointer',
//                   transition: 'background-color 0.2s',
//                   opacity: isLoading ? 0.7 : 1
//                 }}
//               >
//                 {isLoading ? '...' : 'Send'}
//               </button>
//             </div>
//           </div>
//         </div>
//       </main>

//       <footer style={{
//         textAlign: 'center',
//         padding: '20px',
//         color: '#666'
//       }}>
//         <p style={{margin: '5px 0'}}>&copy; 2024 ClinicQ. All rights reserved.</p>
//         <p style={{
//           fontSize: '0.9rem',
//           maxWidth: '800px',
//           margin: '10px auto',
//           lineHeight: '1.4'
//         }}>
//           Disclaimer: This AI Health Assistant is for informational purposes only and should not be considered medical advice. 
//           Always consult with a qualified healthcare professional for medical concerns.
//         </p>
//       </footer>
//     </div>
//   );
// }

// export default ChatBot;
// ChatBot.jsx
import React, { useState, useEffect, useRef } from 'react';
import '../assets/chat.css';

function ChatBot() {
  const [messages, setMessages] = useState([
    { text: "Hello! I'm your AI Health Assistant. How can I help you today?", sender: 'ai' },
  ]);
  const [userInput, setUserInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messageContainerRef = useRef(null);
  
  useEffect(() => {
    setSessionId(Math.random().toString(36).substring(7));
    
    if (messageContainerRef.current) {  
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  async function sendMessage() {
    if (!userInput.trim() && !selectedImage) return;

    const newUserMessage = { text: userInput, sender: 'user', image: selectedImage };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);

    setUserInput('');
    setSelectedImage(null);
    setIsLoading(true);

    try {
      const requestBody = {
        input: userInput,
        session_id: sessionId,
        image: selectedImage ? selectedImage.split(',')[1] : null,
      };

      const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (response.ok) {
        const newAIMessage = { text: data.response, sender: 'ai' };
        setMessages((prevMessages) => [...prevMessages, newAIMessage]);
      } else {
        console.error('Error:', data.error);
        const errorMessage = { 
          text: data.error || "Sorry, I'm having trouble connecting to the server. Please try again.", 
          sender: 'ai' 
        };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
    } catch (error) {
      console.error('Error connecting to server:', error);
      const errorMessage = { 
        text: "Sorry, I'm having trouble connecting to the server. Please try again.", 
        sender: 'ai' 
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        alert('Please select an image smaller than 5MB');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-card">
        <div className="chat-header">
          <span className="header-icon">🏥</span>
          <h1>AI Health Assistant</h1>
          <p>Your personal guide to natural health and wellness</p>
        </div>

        <div className="message-container" ref={messageContainerRef}>
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender}`}>
              {message.image && (
                <div className="message-image">
                  <img src={message.image} alt="Uploaded content" />
                </div>
              )}
              <div className="message-content">
                <p>{message.text}</p>
                <span className="message-time">{new Date().toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="loading-indicator">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>

        <div className="input-container">
          <div className="image-upload">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              id="image-upload"
              className="hidden"
            />
            <label htmlFor="image-upload" className="upload-button">
              📷
            </label>
          </div>

          {selectedImage && (
            <div className="image-preview">
              <img src={selectedImage} alt="Preview" />
              <button 
                onClick={() => setSelectedImage(null)}
                className="remove-image"
              >
                ×
              </button>
            </div>
          )}

          <input
            type="text"
            placeholder="Type your health-related question..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            className="message-input"
          />

          <button 
            onClick={sendMessage}
            disabled={isLoading}
            className="send-button"
          >
            Send
          </button>
        </div>
      </div>

      <footer className="chat-footer">
        <p>&copy; 2024 ClinicQ. All rights reserved.</p>
        <p className="disclaimer">
          Disclaimer: This AI Health Assistant is for informational purposes only and should not be considered medical advice. 
          Always consult with a qualified healthcare professional for medical concerns.
        </p>
      </footer>
    </div>
  );
}

export default ChatBot;