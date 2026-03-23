import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';
import api from "../api/axios";
import { useAuth } from "../auth/AuthContext";

// Use environment variable or default
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export default function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
    const { logout, isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [searchCategory, setSearchCategory] = useState("");
  const [searchValue, setSearchValue] = useState("");
  const [availableValues, setAvailableValues] = useState([]);
  const [loadingValues, setLoadingValues] = useState(false);
  const [filteredRecipes, setFilteredRecipes] = useState([]);

    // Ref to track previous recipe count for polling detection
    const prevRecipeCountRef = useRef(0);

    // Polling interval ref (so we can clear it)
    const pollIntervalRef = useRef(null);

    useEffect(() => {
        fetchRecipes();
    }, []);

  useEffect(() => {
    applyFilter();
  }, [searchValue, searchCategory, recipes]);

  useEffect(() => {
    if (!searchCategory) {
      setAvailableValues([]);
      setSearchValue('');
      setFilteredRecipes(null);
      return;
    }

    const loadValues = async () => {
      setLoadingValues(true);
        try {
        const unique = [...new Set(
          recipes
            .map(r => r[searchCategory])
            .filter(Boolean)
        )].sort();

        setAvailableValues(unique);
      } catch (err) {
        console.error(err);
        setAvailableValues([]);
      } finally {
        setLoadingValues(false);
      }
    };

    loadValues();
  }, [searchCategory, recipes]);

  const applyFilter = () => {
    if (!searchCategory || !searchValue) {
        setFilteredRecipes(null);
      return;
    }
    const filtered = recipes.filter(recipe => {
      const value = recipe[searchCategory];
      if (value === undefined || value === null) return false;
      return String(value).toLowerCase() === searchValue.toLowerCase();
    });
    setFilteredRecipes(filtered);
  };

  const fetchRecipes = async () => {
    try {
      const response = await api.get("/api/recipes");
      if (response.status === 204) {
          setRecipes([]);
          setMessage("You currently do not have any recipes saved. Let's get started!");
        return;
      }
      setRecipes(response.data);
        // Update previous count after successful fetch
        prevRecipeCountRef.current = response.data.length;
    } catch (err) {
      console.error("Error fetching recipes:", err);
      setError("Failed to load recipes");
    }
  };

    // Start polling after upload
    const startPolling = () => {
        // Clear any existing interval
        if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
        }

        // Show processing modal
        Swal.fire({
            title: 'Processing Your Recipe',
            html: 'We are extracting text and saving it to your database...<br>This usually takes 20–60 seconds.',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        pollIntervalRef.current = setInterval(async () => {
            try {
                const res = await api.get("/api/recipes");
                const currentRecipes = res.data || [];

                // If count increased → new recipe arrived
                if (currentRecipes.length > prevRecipeCountRef.current) {
                    clearInterval(pollIntervalRef.current);
                    pollIntervalRef.current = null;

                    setRecipes(currentRecipes);
                    prevRecipeCountRef.current = currentRecipes.length;

                    Swal.fire({
                        title: 'Success!',
                        text: 'Your new recipe is ready and added to the list.',
                        icon: 'success',
                        timer: 2500,
                        showConfirmButton: false
                    });
                }
            } catch (err) {
                console.error("Polling error:", err);
            }
        }, 5000); // Poll every 5 seconds
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post(
        "/api/recipes/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

        // Start polling immediately after 202 response
        startPolling();

      setSelectedFile(null);
        document.getElementById("fileInput").value = "";
    } catch (err) {
        setError(err.response?.data?.error || "Failed to upload recipe");
      Swal.fire({
          title: 'Upload Failed',
          text: err.response?.data?.error || "Something went wrong.",
          icon: 'error'
      });
    } finally {
        setLoading(false);
    }
  };

    // Cleanup polling on unmount
    useEffect(() => {
        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
            }
        };
  }, []);

    // ... rest of your handlers remain the same (handleUrlSubmit, handleDelete, etc.)

  return (
    <div className="App">
          {/* Your existing JSX remains unchanged */}
          {/* ... header, left/right columns, upload forms, recipe grid ... */}
    </div>
  );
}