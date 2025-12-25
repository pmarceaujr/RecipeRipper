import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";

import ForgotPassword from "./pages/ForgotPassword";
import Homepage from "./pages/Homepage";
import Login from "./pages/Login";
import RecipeDetail from "./pages/RecipeDetail";
import RecipeEdit from "./pages/RecipeEdit";
import RecipeList from "./pages/RecipeList";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";

function App() {
  return (
    <Router>
      <Routes>
        {/* Redirect root → login */}
        <Route path="/" element={<Homepage />} />        
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        <Route
          path="/recipes"
          element={
            <ProtectedRoute>
              <RecipeList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recipe/:id"
          element={
            <ProtectedRoute>
              <RecipeDetail />
            </ProtectedRoute>
          }
        />

        <Route
          path="/recipe/:id/edit"
          element={
            <ProtectedRoute>
              <RecipeEdit />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
