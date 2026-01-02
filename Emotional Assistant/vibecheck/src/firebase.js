// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, browserSessionPersistence, setPersistence  } from "firebase/auth";

// import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyB8_MTu8mQwluzovo-EaNDeltdAAHO-080",
  authDomain: "vibecheck-cff5c.firebaseapp.com",
  projectId: "vibecheck-cff5c",
//   storageBucket: "vibecheck-cff5c.firebasestorage.app",
  storageBucket: "vibecheck-cff5c.appspot.com",
  messagingSenderId: "122228370006",
  appId: "1:122228370006:web:bea2a576124a06bea229f7",
  measurementId: "G-8GNZRYT4HZ"
};


// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

// export const analytics = getAnalytics(app);

// 🔥 Set session to expire when browser/tab is closed
setPersistence(auth, browserSessionPersistence)
  .then(() => {
    console.log("Session persistence set to session-only.");
  })
  .catch((error) => {
    console.error("Persistence error:", error);
  });

  

// // src/firebase.js
// import { initializeApp } from "firebase/app";
// // import { getAuth } from "firebase/auth";
// import { auth } from "./firebase";


// const firebaseConfig = {
//   apiKey: "AIzaSyB8_MTu8mQwluzovo-EaNDeltdAAHO-080",
//   authDomain: "vibecheck-cff5c.firebaseapp.com",
//   projectId: "vibecheck-cff5c",
//   storageBucket: "vibecheck-cff5c.appspot.com",
//   messagingSenderId: "122228370006",
//   appId: "1:122228370006:web:bea2a576124a06bea229f7",
//   measurementId: "G-8GNZRYT4HZ",
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);

// // Initialize Authentication
// export const auth = getAuth(app);
