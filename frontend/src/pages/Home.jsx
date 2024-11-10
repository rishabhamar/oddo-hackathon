import { Link } from "react-router-dom";
import aibot from "../assets/aibot.jpeg";
import doctor from "../assets/doctor.jpeg";


function Home(){
    return (
        <>
    <section className="hero">
        <h2>Your Health, Our Priority</h2>
        <p>Get instant medical advice and connect with top doctors online.</p>
        <div className="hero-buttons">
            <Link  to="/signUp"><button className="signup">Sign Up</button></Link>
            <Link to="/login"><button className="login">Log In</button></Link>
        </div>
    </section>

<section className="features-section">
  <div className="features">
      <div className="feature-card schedule">
          <h3>📅Schedule Appointment</h3>
          <p>Book your next doctor's visit with ease.</p>
          <button>Schedule Now</button>
      </div>
      <div className="feature-card message">
          <h3>💬Message Doctor</h3>
          <p>Communicate directly with your healthcare provider.</p>
          <button>Start Chat</button>
      </div>
      <div className="feature-card reminders">
          <h3>🔔Health Reminders</h3>
          <p>Stay on top of your health with personalized reminders.</p>
          <button>Set Reminders</button>
      </div>
  </div>
</section>

<section className="consult-assistant">
  <div className="card consult-card">
    <h4>Consult with Doctors</h4>
    <img src={doctor} alt="Consult with Doctors" className="service-image" />
    <p>Connect with experienced healthcare professionals for personalized medical advice.</p>
    <button className="button consult-button">Book Consultation</button>
  </div>
  
  <div className="card assistant-card">
    <h4>AI Health Assistant</h4>
    <img src={aibot} alt="AI Health Assistant" className="service-image" />
    <p>Get instant answers to your health queries with our AI-powered chatbot.</p>
    <Link to="/chatbot"><button className="button assistant-button">Chat Now</button></Link>
  </div>
</section>


   <h1 >Our Services</h1>

<section className="additional-services">
    <div className="service-card service-card-blue">
        <h4><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="lucide lucide-file-text mr-2 h-5 w-5 text-blue-600" data-id="80"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>Medical Records</h4>
        <p>Access and manage your medical records securely online.</p>
    </div>
    <div className="service-card service-card-green">
        <h4><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="lucide lucide-pill mr-2 h-5 w-5 text-green-600" data-id="86"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"></path><path d="m8.5 8.5 7 7"></path></svg>Prescription Refills</h4>
        <p>Request prescription refills and manage your medications easily.</p>
    </div>
    <div className="service-card service-card-purple">
        <h4><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="lucide lucide-activity mr-2 h-5 w-5 text-red-600" data-id="92"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>Health Monitoring</h4>
        <p>Track your health metrics and receive personalized insights.</p>
    </div>
</section>
    
    <footer>
        <div className="container">
            <p>&copy; 2024 ClinicQ. All rights reserved.</p>
            <nav>
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Contact</a>
            </nav>
        </div>
    </footer>


        </>
    );
}

export default Home