

import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
<header>
      <div className="container">
          <h1 className="logo">ClinicQ</h1>
          <nav>
              <NavLink to="/">Home</NavLink>
              <a href="#">Services</a>
              <a href="#">Doctors</a>
              <NavLink to="/about">About</NavLink> 
          </nav>
      </div>
  </header>
  );
};

export default Navbar;