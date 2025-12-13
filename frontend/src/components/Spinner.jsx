const Spinner = ({ size = 'md', color = 'indigo' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-4',
    lg: 'h-12 w-12 border-4',
  };

  const colorClasses = {
    indigo: 'border-indigo-600',
    white: 'border-white',
    gray: 'border-gray-900',
  };

  return (
    <div className="flex justify-center items-center">
      <div
        className={`animate-spin rounded-full border-t-transparent ${sizeClasses[size]} ${colorClasses[color]}`}
      ></div>
    </div>
  );
};

export default Spinner;
