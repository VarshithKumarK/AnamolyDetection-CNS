/**
 * Mock Auth Utility for Development
 *
 * Usage:
 * Import logic from here if you want to bypass backend for testing UI states.
 * Or run this in console to simulate events.
 */

export const mockUser = {
  name: "Test User",
  email: "test@example.com",
  id: "user_12345",
  avatar: null,
};

export const mockToken = "mock_jwt_token_123456789";

export const simulateLogin = () => {
  localStorage.setItem("token", mockToken);
  localStorage.setItem("user", JSON.stringify(mockUser));
  window.location.reload();
};

export const simulateLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.reload();
};

// Expose to window for easy console access
if (typeof window !== "undefined") {
  window.mockAuth = {
    login: simulateLogin,
    logout: simulateLogout,
    user: mockUser,
  };
  console.log(
    "Mock Auth Loaded. Use window.mockAuth.login() or window.mockAuth.logout()"
  );
}
