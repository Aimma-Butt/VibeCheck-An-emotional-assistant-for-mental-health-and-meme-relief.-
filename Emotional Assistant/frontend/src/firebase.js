// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, browserSessionPersistence, setPersistence  } from "firebase/auth";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "your_api_key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your_project_id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "your_sender_id",
  appId: "your_app_id",
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
