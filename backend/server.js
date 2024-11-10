const express = require('express');
const firebaseAdmin = require('firebase-admin');
const firebase = require('firebase/app');
require('firebase/auth');
const bodyParser = require('body-parser');
const cors = require('cors')

// Initialize Firebase Admin SDK for server-side operations
const serviceAccount = require('./firebase-config.json');
firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(serviceAccount),
});

// Initialize Firebase Client SDK for client-side authentication
const firebaseConfig = {
    apiKey: "AIzaSyAGe-NtaKqIbWBPUvxeW2idwSs2h8wbtUQ",
    authDomain: "my-first-app-64106.firebaseapp.com",
    projectId: "my-first-app-64106",
    storageBucket: "my-first-app-64106.firebasestorage.app",
    messagingSenderId: "903736527485",
    appId: "1:903736527485:web:f46d57510cf7d93b0eff14"
};

firebase.initializeApp(firebaseConfig);

const app = express();
app.use(cors());

app.use(bodyParser.json());

// Sign-up Endpoint
app.post('/api/user/signup', async (req, res) => {
  const { email, password, role, name, degree, specialization, experience, clinicAddress } = req.body;

  try {
    // Create the user with email and password in Firebase Authentication
    const userRecord = await firebaseAdmin.auth().createUser({
      email,
      password,
      displayName: role === 'doctor' ? 'Doctor' : 'User',
    });

    // Add custom user data to Firestore based on role
    const db = firebaseAdmin.firestore();
    const userDoc = db.collection('users').doc(userRecord.uid);

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

    res.status(201).json({ message: 'User created successfully', userId: userRecord.uid });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Login Endpoint
app.post('/api/user/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const userCredential = await firebase.auth().signInWithEmailAndPassword(firebase.getAuth(), email, password);
    const token = await userCredential.user.getIdToken();

    res.status(200).json({ message: 'Login successful', token });
  } catch (error) {
    res.status(400).json({ error: 'Invalid email or password' });
  }
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
