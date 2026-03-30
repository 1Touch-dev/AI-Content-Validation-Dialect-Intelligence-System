"use client";

const TOKEN_KEY = "backend_access_token";
const USERNAME_KEY = "backend_username";

export function backendBaseUrl() {
  return process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || "https://api.theinvictus.group";
}

export function setAuthSession(token: string, username: string) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

export function clearAuthSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function getUsername() {
  return localStorage.getItem(USERNAME_KEY) || "";
}

export async function backendFetch(path: string, init: RequestInit = {}) {
  const token = getAccessToken();
  const headers = new Headers(init.headers || {});
  const hasExplicitContentType = headers.has("Content-Type");
  const isFormData = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!hasExplicitContentType && !isFormData) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(`${backendBaseUrl()}${path}`, {
    ...init,
    headers,
  });
}
