import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            AI Reader Agent
          </Link>
          <nav className="flex space-x-6">
            <Link
              to="/"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Home
            </Link>
            <Link
              to="/reader"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Reader
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
