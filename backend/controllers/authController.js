const admin = require('../config/firebase');

// Sign Up
exports.registerUser = async (req, res) => {
  const { email, password, displayName } = req.body;
  try {
    const userRecord = await admin.auth().createUser({
      email,
      password,
      displayName,
    });
    const token = await admin.auth().createCustomToken(userRecord.uid);
    res.status(201).json({ uid: userRecord.uid, email: userRecord.email, displayName: userRecord.displayName, token });
  } catch (error) {
    res.status(400).json({ message: 'Error creating user', error: error.message });
  }
};

// Login
exports.authUser = async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await admin.auth().getUserByEmail(email);
    const token = await admin.auth().createCustomToken(user.uid);
    res.json({ uid: user.uid, email: user.email, displayName: user.displayName, token });
  } catch (error) {
    res.status(401).json({ message: 'Invalid credentials', error: error.message });
  }
};

// Logout
exports.logoutUser = (req, res) => {
  // Note: Firebase authentication is stateless. Logging out on the client just requires token deletion.
  res.json({ message: 'Logged out successfully' });
};
