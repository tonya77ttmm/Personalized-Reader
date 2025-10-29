import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="max-w-4xl mx-auto text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-6">
        Welcome to AI Reader Agent
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        Upload text documents and get AI-powered explanations for difficult
        content. Enhance your reading comprehension with personalized
        assistance.
      </p>
      <div className="space-y-4">
        <Link
          to="/reader"
          className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          Start Reading
        </Link>
        <div className="text-sm text-gray-500">
          Upload a text file to begin your enhanced reading experience
        </div>
      </div>
    </div>
  );
};

export default Home;
