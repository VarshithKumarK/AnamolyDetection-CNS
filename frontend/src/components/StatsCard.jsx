const StatsCard = ({ title, value, icon: Icon, color }) => {
  // Extract tailwind color name to use for background opacity if possible, or just default to gray-800
  // Simple check to determine bg color based on text color class
  const getBgColor = (colorClass) => {
      if (colorClass.includes('red')) return 'bg-red-500/10';
      if (colorClass.includes('green')) return 'bg-green-500/10';
      if (colorClass.includes('blue')) return 'bg-blue-500/10';
      if (colorClass.includes('yellow')) return 'bg-yellow-500/10';
      return 'bg-indigo-500/10';
  };

  return (
    <div className="card hover:border-white/20 transition-all duration-300 group">
      <div className="flex items-center">
        <div className={`p-4 rounded-xl ${getBgColor(color)} group-hover:scale-110 transition-transform duration-300`}>
          <Icon className={`h-6 w-6 ${color}`} aria-hidden="true" />
        </div>
        <div className="ml-5">
          <p className="text-sm font-medium text-gray-400">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
