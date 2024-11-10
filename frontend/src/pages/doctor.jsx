import React from "react";
import { useNavigate } from "react-router-dom";

import '../assets/doctor.css';


const doctors = [
  {
    id: 1,
    name: "Dr. Jane Smith",
    photo: "/placeholder.svg",
    experience: "10 years",
    specialty: "Cardiology",
    degree: "MD, FACC",
    available: true,
    rating: 4.8,
  },
  { 
    id: 2,
    name: "Dr. John Doe",
    photo: "/placeholder.svg",
    experience: "15 years",
    specialty: "Neurology",
    degree: "MD, PhD",
    available: false,
    rating: 4.9,
  },
  {
    id: 3,
    name: "Dr. Emily Brown",
    photo: "/placeholder.svg",
    experience: "8 years",
    specialty: "Pediatrics",
    degree: "MD, FAAP",
    available: true,
    rating: 4.7,
  },
  {
    id: 4,
    name: "Dr. Michael Chen",
    photo: "/placeholder.svg",
    experience: "12 years",
    specialty: "Orthopedics",
    degree: "MD, FAAOS",
    available: false,
    rating: 4.6,
  },
];

export default function DoctorsAvailability() {
  return (
    <div className="container">
      <h1 className="title">Our Doctors</h1>
      <div className="doctor-grid">
        {doctors.map((doctor) => (
          <div key={doctor.id} className="card">
            <img
              src={doctor.photo}
              alt={`${doctor.name}'s profile photo`}
              className="photo"
            />
            <span
              className={`badge ${doctor.available ? "available" : "unavailable"}`}
            >
              {doctor.available ? "Available" : "Unavailable"}
            </span>
            <div className="content">
              <h2 className="name">{doctor.name}</h2>
              <p className="specialty">{doctor.specialty}</p>
              <p className="degree">{doctor.degree}</p>
              <p className="experience">{doctor.experience} experience</p>
              <div className="rating">⭐ {doctor.rating.toFixed(1)}</div>
              <div className="actions">
                <button className="appoint-button" disabled={!doctor.available}>
                  Appoint
                </button>
                <button className="rate-button">Rate</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
