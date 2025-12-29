// src/components/ImportLogo.js   (or similar path)
import recipeRipperLogo from '../assets/images/recipe_ripper_logo.png';

function Logo({ className = '', ...props }) {
  return (
    <img
      src={recipeRipperLogo}
      alt="Recipe Ripper Logo"
      className={`h-10 w-auto ${className}`}
      {...props}
    />
  );
}

export default Logo;          // ← default export (common & recommended)