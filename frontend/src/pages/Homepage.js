import { Link, useNavigate } from "react-router-dom";
import "../assets/css/LandingPage.css";

export default function LandingPage() {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/login");
  };

    const handleRegister = () => {
    navigate("/register");
  };

  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1>Welcome to The Recipe Ripper Database!</h1>
        <p>Your personal place on the web to store, organize and search your favorite recipes.</p>



        {/* Link to React login page */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
        <button className="landing-button" onClick={handleLogin} style={{ width: '125px' }} >
          Login
        </button>
        <button className="landing-button" onClick={handleRegister} style={{ width: '125px' }}>
          Register
        </button>
        </div>
        <div > {/* stuffing div */}
          <p>We "rip" the key content from the recipes you love and remove all the "stuffing."</p>

          {/* </div>         */}
          {/* Video placeholder */}
          <div className="video-grid">

            {/* Main container with two columns */}
            <div className="video-column">
              {/* Left column */}

              <h3 style={{
                marginBottom: '12px',
                fontSize: '1.4rem',
                fontWeight: '400',
              }}>
                Go from this....
              </h3>


              <video width="100%" autoPlay loop muted playsInline
                style={{
                  borderRadius: '12px',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.25)',
                  width: '100%',
                  maxWidth: '500px',
                  height: 'auto',
                  display: 'block',
                  margin: '0 auto'
                }}>
                <source src="/assets/videos/blog_video.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>

            </div>
            <div className="video-column">
            {/* Right column */}

              <h3 style={{
                marginBottom: '12px',
                fontSize: '1.4rem',
                fontWeight: '400',
              }}>
                ....to this!
              </h3>
              <video width="100%" autoPlay loop muted playsInline
                style={{
                borderRadius: '12px',
                boxShadow: '0 8px 25px rgba(0,0,0,0.25)',
                width: '100%',
                maxWidth: '500px',
                height: 'auto',
                display: 'block',
                margin: '0 auto'
              }}>
                <source src="/assets/videos/Content_only.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div> {/* End main container */}
      </div> {/* End video placeholder */}

    </div> /* End stuffing div */

  );
}
