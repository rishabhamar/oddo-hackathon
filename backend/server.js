const express = require('express');
const firebaseAdmin = require('firebase-admin');
const { initializeApp } = require('firebase/app');
const { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } = require('firebase/auth');
const bodyParser = require('body-parser');
const cors = require('cors');

// Initialize Firebase Admin SDK
const serviceAccount = require('./fire_config.json');
firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(serviceAccount),
});

// Initialize Firebase App with config


const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Sign-up Endpoint
app.post('/api/user/signup', async (req, res) => {
  const { email, password, role, name, degree, specialization, experience, clinicAddress } = req.body;

  try {
    // Create user with email/password
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Store additional user data in Firestore
    const db = firebaseAdmin.firestore();
    const userDoc = db.collection('users').doc(user.uid);

    if (role === 'doctor') {
      await userDoc.set({
        role,
        email,
        degree,
        specialization, 
        experience,
        clinicAddress,
      });
    } else {
      await userDoc.set({
        role,
        email,
        name,
      });
    }

    // Get auth token
    const token = await user.getIdToken();

    res.status(201).json({ 
      message: 'User created successfully',
      userId: user.uid,
      token
    });

  } catch (error) {
    console.error('Signup error:', error);
    res.status(400).json({ error: error.message });
  }
});

// Login Endpoint
app.post('/api/user/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken();

    res.status(200).json({
      message: 'Login successful',
      token,
      userId: userCredential.user.uid
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(400).json({ error: error.message });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
