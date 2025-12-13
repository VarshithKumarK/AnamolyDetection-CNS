export const formatScore = (score) => {
  if (score === undefined || score === null) return "-";
  return Number(score).toFixed(4);
};

export const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleDateString();
};
