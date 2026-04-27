import React, { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css'; // optional but makes it look nice
import api from "../api/axios";
import { useAuth } from "../auth/AuthContext";
// import { showAlert } from "../utils/alerts";

// import "../App.css";

// Use environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL 

export default function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [message, setMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const { logout, isLoggedIn } = useAuth();
  const navigate = useNavigate();
  // Search filter states
  const [searchCategory, setSearchCategory] = useState("");
  const [searchValue, setSearchValue] = useState("");

  // New picklist states
  const [courseValues, setCourseValues] = useState([]);
  const [cuisineValues, setCuisineValues] = useState([]);
  const [primaryValues, setPrimaryValues] = useState([]);

  // Pagination logic
  const [recipesPerPage, setRecipesPerPage] = useState(() => {
    const saved = localStorage.getItem('recipesPerPage');
    return saved ? Number(saved) : 10; // default 10
  });

  // Configurable constants for pagination
  const recipesToShow = recipes;
  const totalRecipes = recipesToShow.length;
  const totalPages = Math.ceil(totalRecipes / recipesPerPage);
  const startIndex = (currentPage - 1) * recipesPerPage;
  const endIndex = startIndex + recipesPerPage;
  const paginatedRecipes = recipesToShow.slice(startIndex, endIndex);

  // Refs for polling
  const prevRecipeCountRef = useRef(0);
  const pollIntervalRef = useRef(null);

  // Load picklist values ONCE
  const refreshPicklistValues = async () => {
    const [courses, cuisines, primary] = await Promise.all([
      api.get("/api/recipe-values?type=course").then(r => r.data),
      api.get("/api/recipe-values?type=cuisine").then(r => r.data),
      api.get("/api/recipe-values?type=primary_ingredient").then(r => r.data)
    ]);

    setCourseValues(courses);
    setCuisineValues(cuisines);
    setPrimaryValues(primary);
  };
  useEffect(() => {
    const loadValues = async () => {
      await refreshPicklistValues();
    };
    loadValues();
  }, []);


  // Build query string based on selected filter
  const buildQueryString = () => {
    const params = new URLSearchParams();
    // params.append("user_id", userId);
    if (searchCategory === "title" && searchValue) {
      params.append("title", searchValue);
    }
    if (searchCategory === "ingredients" && searchValue) {
      params.append("ingredient", searchValue);
    }
    if (searchCategory === "course" && searchValue) {
      params.append("course", searchValue);
    }
    if (searchCategory === "cuisine" && searchValue) {
      params.append("cuisine", searchValue);
    }
    if (searchCategory === "primary_ingredient" && searchValue) {
      params.append("primary-ingredient", searchValue);
    }
    return params.toString();
  };

  useEffect(() => {
    if (searchCategory === "") {
      fetchRecipes();   // reload all recipes
    }
  }, [searchCategory]);


  // Fetch recipes from backend
  const fetchRecipes = async () => {
    setLoading(true);
    setMessage(null);
    setUploadError(null);
    setError(null);
    try {
      const query = buildQueryString();
      const response = await api.get(`/api/recipes?${query}`);
      if (response.status === 200 && response.data.msg) {
        // Handle "no content" case – show your message
        setRecipes([]); // or set a flag
        setMessage(response.data.msg)
        // setMessage("You currently do not have any recipes saved.  Let's get started!");
        return;
      }
      else if (response.status === 204) {
        setRecipes([]); // or set a flag
        setMessage("You currently do not have any recipes saved.  Let's get started!");
      }

      console.log("Fetched recipes:", response.config.headers);
      setRecipes(response.data);
      prevRecipeCountRef.current = response.data.length;
    } catch (err) {
      console.error("Error fetching recipes:", err);
      setError("Failed to load recipes");
    } finally {
      setLoading(false);
    }
  };

  // Fetch on first load
  useEffect(() => {
    fetchRecipes();
  }, []);

  // Fetch whenever filters change
  useEffect(() => {
    if (searchCategory && searchValue !== "") {
      const timeout = setTimeout(() => fetchRecipes(), 300);
      return () => clearTimeout(timeout);
    }
  }, [searchCategory, searchValue]);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleLogin = () => {
    logout();
    navigate("/login");
  };  



  useEffect(() => {
    const loadValues = async () => {
      const [courses, cuisines, primary] = await Promise.all([
        api.get("/api/recipe-values?type=course").then(r => r.data),
        api.get("/api/recipe-values?type=cuisine").then(r => r.data),
        api.get("/api/recipe-values?type=primary_ingredient").then(r => r.data)
      ]);
      setCourseValues(courses);
      setCuisineValues(cuisines);
      setPrimaryValues(primary);
    };

    loadValues();
  }, []);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  // Start polling after upload
  const startPolling = (jobId) => {
    if (!jobId) {
      console.error("No jobId provided for polling");
      Swal.fire({
        title: 'Error',
        text: 'Could not track processing status. <br>Please try your upload again.',
        icon: 'error'
      });
      return;
    }   
    // Clear any existing interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    // Show processing modal
    Swal.fire({
      title: 'Processing Your Recipe',
      html: 'Extracting text and saving it to your database...<br>This usually takes 20-40 seconds.',
      allowOutsideClick: false,
      allowEscapeKey: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    let pollingAttempts = 0;
    const MAX_ATTEMPTS = 36;
    pollIntervalRef.current = setInterval(async () => {
      try {
        pollingAttempts++;
        const res_recipes = await api.get("/api/recipes");
        const currentRecipes = res_recipes.data || [];
        const res_status = await api.get(`/api/job-status/${jobId}`);
        const status = res_status.data.status;

        // If count increased → new recipe arrived
        if (currentRecipes.length > prevRecipeCountRef.current && status === "completed") {
          clearInterval(pollIntervalRef.current);
          refreshPicklistValues();
          setMessage(null);

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
        else if (status === 'error') {
          console.log(`Polling error status ${status} for job ${jobId}...`);
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;

          Swal.fire({
            title: 'Processing Failed',
            text: res_status.data.error || 'Failed to process the recipe. Please try again. - ' || res_recipes.data.error || ' - An unknown error occurred.',
            icon: 'error',
            confirmButtonText: 'OK'
          });
        }
        else if (pollingAttempts === 6) {
          console.log(`Polling error 6 times ${pollingAttempts} for job ${jobId}...`);
            // Show still processing modal
            Swal.fire({
              title: 'Processing Your Recipe',
              html: 'Still extracting text... at 30 seconds.  <br>This must be a little more complex than typical recipes.',
              allowOutsideClick: false,
              allowEscapeKey: false,
              showConfirmButton: false,
              didOpen: () => {
                Swal.showLoading();
              }
            });
          }
        else if (pollingAttempts === 12) {
          console.log(`Polling error 12 times ${pollingAttempts} for job ${jobId}...`);
          // Show still processing it must be a big one
          Swal.fire({
            title: 'Processing Your Recipe',
            html: 'Still extracting text... at 60 seconds.  <br>This must be a complex extraction, it usually does not take this long.',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => {
              Swal.showLoading();
            }
          });
        }
        else if (pollingAttempts >= MAX_ATTEMPTS) {
          console.log(`Polling error MAX times ${pollingAttempts} for job ${jobId}...`);
          // Timeout protection
          clearInterval(pollIntervalRef.current);
          Swal.fire({
            title: 'Taking Too Long',
            text: 'The job is taking longer than expected. Please refresh the page later to check.',
            icon: 'info'
          });
        };       

      } catch (err) {
        if (err.response.data.error === "Website prevents scraping, print to PDF and upload as a file.") {
          console.log(`Website prevents scraping, print to PDF and upload as a file.`);
          clearInterval(pollIntervalRef.current);
          Swal.fire({
            title: 'Website Prevents Scraping',
            text: 'The web site prevents scraping. Please print the recipe to a PDF and upload the PDF as a file.',
            icon: 'info'
          });
        }
        else {
          console.error("Polling error:", err);
          clearInterval(pollIntervalRef.current);
          Swal.fire({
            title: 'Error',
            text: 'An error occurred while checking the job status. Please try again.',
            icon: 'error'
          });

        }
      }
    }, 5000); // Poll every 5 seconds
  };



  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setUploadError("");
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    setUploadError("");
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post(
        "/api/recipes/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      const jobId = response.data.job_id;

      if (jobId) {
        startPolling(jobId);
      } else {
        Swal.fire('Warning', 'Upload started but no tracking ID received.', 'warning');
        await fetchRecipes();
      }    
      setSelectedFile(null);
      document.getElementById("fileInput").value = "";
      await fetchRecipes();
    } catch (err) {
      setUploadError(err.response?.data?.error || "Failed to upload recipe");
    }

    setLoading(false);
  };

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setUploadError("");

    try {
      const response = await api.post(
        "/api/recipes/from-url",
        { url }
      );
      console.log(response)
      const jobId = response.data.job_id;

      if (jobId) {
        startPolling(jobId);
      } else {
        Swal.fire('Warning', 'Upload started but no tracking ID received.', 'warning');
        await fetchRecipes();
      }       
      setUrl("");
      await fetchRecipes();
    } catch (err) {
      setUploadError(err.response?.data?.error || "Failed to add recipe from URL");
    }

    setLoading(false);
  };

  const handleDelete = async (id, title) => {
    // Optional: early return if no id (defensive)
    if (!id) return;

    const result = await Swal.fire({
      title: 'Delete recipe?',
      html: `Are you sure you want to permanently delete<br><strong>"${title}"</strong>?`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      reverseButtons: true,              // puts dangerous action on right
      focusCancel: true,                 // better accessibility
      allowOutsideClick: () => !Swal.isLoading(), // prevent closing while loading
    });

    if (!result.isConfirmed) return;

    try {
      await api.delete(`${API_URL}/api/recipe/${id}`);
      await fetchRecipes();
    } catch (err) {
      setError("Failed to delete recipe");
    }
  };

  const handleEdit = async (id, title) => {
    // if (!window.confirm(`Delete "${title}"?`)) return;

    try {
      navigate(`/recipe/${id}/edit`);
      // await fetchRecipes();
    } catch (err) {
      setError(`Failed to navigate to edit page for "${title}".`);
    }
  };
  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">

          <h1>🍳 The Recipe Ripper Database <span style={{ fontSize: ".27EM" }}>v:7.5.2 - 04-24-2026:11:46</span></h1> 
          <button className="auth-button"
            onClick={isLoggedIn ? handleLogout : handleLogin}
        >
            {isLoggedIn ? "Logout" : "Login"}
          </button>
        </div>
      </header>   

      <div className="container">
        {/* LEFT SIDE */}
        <div className="left">
          <div className="add-recipe-section">
            <h2>Add New Recipe</h2>

            {uploadError && <div className="error-message">{error}</div>}
            {/* {message && !error && <div className="status-message">{message}</div>} */}

            {/* File Upload */}
            <div className="upload-option">
              <h3>📁 Upload File</h3>
              <p className="file-info">Supports: TXT, PDF, JPG, PNG</p>

              <input
                id="fileInput"
                type="file"
                onChange={handleFileChange}
                accept=".txt,.pdf,.jpg,.jpeg,.png"
                disabled={loading}
              />

              {selectedFile && (
                <div>
                  <p>Selected: {selectedFile.name}</p>
                  <button style={{ width: "165px" }} onClick={handleFileUpload} disabled={loading}>
                    {loading ? "Processing..." : "Upload & Parse"}
                  </button>
                </div>
              )}
            </div>

            {/* URL Input */}
            <div className="upload-option">
              <h3>🔗 Add from URL</h3>
              <p>By importing a recipe, you confirm this content is for your personal use only.</p>

              <form onSubmit={handleUrlSubmit}>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/recipe"
                  disabled={loading}
                  required
                />

                <button style={{ width: "135px" }} type="submit" disabled={loading}>
                  {loading ? "Processing..." : "Add Recipe"}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="right">
          <div className="recipe-section">
            {/* Changed: header + search on one line */}
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1.2rem',
                flexWrap: 'wrap',
                gap: '1rem'
              }}
            >
              <h2 style={{ margin: 0 }}>
                My Recipes ({recipes.length})</h2>


              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>   {/* ──→  New search controls start here  ──→ */}

                <select
                  value={searchCategory}
                  onChange={(e) => {
                    setSearchCategory(e.target.value);
                    setSearchValue('');
                    // setSearchValue(''); // reset second field when category changes
                  }}
                  style={{ padding: '0.5rem', minWidth: '140px', fontSize: '1rem' }}
                >
                  <option value="">All categories</option>
                  <option value="title">Recipe Title</option>
                  <option value="ingredients">Ingredients</option>
                  <option value="course">Course</option>
                  <option value="cuisine">Cuisine</option>
                  <option value="primary_ingredient">Main Ingredient</option>
                  {/* Add more filter types later if needed */}
                </select>

                {(() => {

                  if (searchCategory === "title") {
                    return (
                      <input
                        type="text"
                        value={searchValue}
                        onChange={(e) => setSearchValue(e.target.value)}
                        placeholder="Recipe title contains..."
                        style={{ padding: '0.5rem', minWidth: '180px', fontSize: '1rem' }}
                      />
                    );
                  }

                  if (searchCategory === "ingredients") {
                    return (
                      <input
                        type="text"
                        value={searchValue}
                        onChange={(e) => setSearchValue(e.target.value)}
                        placeholder="Ingredients contain..."
                        style={{ padding: '0.5rem', minWidth: '180px', fontSize: '1rem' }}
                      />
                    );
                  }

                  // Dropdown categories
                  return (
                    <select
                      value={searchValue}
                      style={{ padding: '0.5rem', minWidth: '180px', fontSize: '1rem' }}
                      onChange={(e) => setSearchValue(e.target.value)}
                      disabled={!searchCategory}
                    >
                      <option value="">Select value...</option>

                      {searchCategory === "course" &&
                        courseValues.map((val) => (
                          <option key={val} value={val}>{val}</option>
                        ))}

                      {searchCategory === "cuisine" &&
                        cuisineValues.map((val) => (
                          <option key={val} value={val}>{val}</option>
                        ))}

                      {searchCategory === "primary_ingredient" &&
                        primaryValues.map((val) => (
                          <option key={val} value={val}>{val}</option>
                        ))}
                    </select>
                  );
                })()}


              </div>  {/* ←─  New search controls end here  ←─ */}

            </div>            


            {loading && <p className="loading">Loading...</p>}
            {error && <p className="error-message">{error}</p>}
            {message && <p className="status-message">{message}</p>}            

            <div className="recipes-grid">
              {/* Add this line for better UX */}
              {/* {filteredRecipes !== null && ( */}
              {paginatedRecipes.length === 0 && totalRecipes > 0 && (  
                <p style={{ color: "#555", marginBottom: "1rem" }}>
                  Showing {recipes.length} filtered recipe(s)
                  {recipes.length === 0 && " — no matches"}
                </p>
              )}

              {/* {(filteredRecipes !== null ? filteredRecipes : recipes).map((recipe) => ( */}
              {paginatedRecipes && paginatedRecipes.length > 0 ? (
                paginatedRecipes.map((recipe) => (
                <div key={recipe.id} className="recipe-card">
                  <div className="recipe-header">
                    <h4>
                      <Link to={`/recipe/${recipe.id}`}>
                        {recipe.title}
                      </Link>
                    </h4>


                  </div>

                  <p className="recipe-category">
                    <strong>Course:</strong>{" "}
                    {recipe.course} {" "}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Cuisine:</strong>{" "}
                    {recipe.cuisine}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Main Ingredient:</strong>{" "}
                    {recipe.primary_ingredient} {""}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Total Time:</strong>{" "}
                    {recipe.total_time}                    
                  </p>

                  {recipe.recipe_source && (
                    <p className="recipe-source">
                      <strong>Source:</strong>{" "}
                      {recipe.is_url === 1 ? (
                        recipe.recipe_source
                      ) : (
                        <a
                          href={recipe.recipe_source}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View URL
                        </a>
                      )}
                    </p>
                  )}
                    <div className="recipe-actions">
                      <div className="tooltip">
                      <button className="edit-btn" onClick={() => handleEdit(recipe.id)} title="Edit">✏️</button>
                      </div>
                      <div className="tooltip">
                      <button className="delete-btn" onClick={() => handleDelete(recipe.id, recipe.title)} title="Delete">🗑️</button>
                    </div>
                    </div>                  
                </div>
                )
                )
              )
                : (<p style={{ padding: "1rem", fontStyle: "italic" }}>
                  No recipes found.
                </p>)
              }
              {/* </div> */}
              {/* ── Pagination Controls ── */}
              {totalPages > 1 && (
                <div className="pagination" style={{ marginTop: '2rem', textAlign: 'center' }}>
                  <button
                    onClick={() => goToPage(currentPage - 1)}
                    disabled={currentPage === 1}
                    style={{ margin: '0 8px', padding: '8px 16px' }}
                  >
                    Previous
                  </button>

                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                    <button 
                      className="page-btn" 
                      style={{
                        background: currentPage === page ? '#3085d6' : '#f0f0f0',
                        color: currentPage === page ? 'white' : 'black',
                      }}   
                      key={page}
                      onClick={() => goToPage(page)}>
                      {page}
                    </button>
                  ))}

                  <button
                    onClick={() => goToPage(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    style={{ margin: '0 8px', padding: '8px 16px' }}
                  >
                    Next
                  </button>
                  <div style={{ marginTop: '1rem', color: '#555', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
                    <span>
                      Showing {startIndex + 1}–{Math.min(endIndex, totalRecipes)} of {totalRecipes}
                    </span>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      Recipes per page:
                      <select
                        value={recipesPerPage}
                        onChange={(e) => {
                          const newSize = Number(e.target.value);
                          setRecipesPerPage(newSize);
                          // Reset to page 1 if current page would be out of range
                          const newTotalPages = Math.ceil(totalRecipes / newSize);
                          if (currentPage > newTotalPages) {
                            setCurrentPage(1);
                          }
                          // Optional: save preference
                          localStorage.setItem('recipesPerPage', newSize);
                        }}
                        style={{ padding: '6px', fontSize: '1rem', borderRadius: '4px' }}
                      >
                        <option value={5}>5</option>
                        <option value={7}>7</option>
                        <option value={8}>8</option>
                        <option value={9}>9</option>
                        <option value={10}>10</option>
                        <option value={15}>15</option>
                        <option value={20}>20</option>
                      </select>
                    </label>
                  </div>
                </div>
              )}
            </div>            
          </div>
        </div>
      </div>
    </div>
  );
}