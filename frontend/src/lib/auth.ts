
import { apiFetch } from "@/lib/api";
import type { User } from "@/lib/types";

export async function getCurrentUser(): Promise<User> {
  return apiFetch<User>("/api/v1/auth/me");
}

export async function logout(): Promise<void> {
  await apiFetch<void>("/api/v1/auth/logout", {
    method: "POST",
  });
}
