import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.brand}>
        HireHub
      </Link>
      <div style={styles.links}>
        <Link to="/">Jobs</Link>
        {user?.role === "candidate" && <Link to="/applications">My Applications</Link>}
        {(user?.role === "recruiter" || user?.role === "admin") && (
          <Link to="/dashboard">Recruiter Dashboard</Link>
        )}
        {user ? (
          <>
            <span style={styles.userTag}>
              {user.full_name} ({user.role})
            </span>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Log in</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

const styles: Record<string, React.CSSProperties> = {
  nav: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 24px",
    borderBottom: "1px solid #e2e2e2",
  },
  brand: { fontWeight: 700, fontSize: "1.2rem", textDecoration: "none", color: "#111" },
  links: { display: "flex", gap: "16px", alignItems: "center" },
  userTag: { color: "#555", fontSize: "0.9rem" },
};
