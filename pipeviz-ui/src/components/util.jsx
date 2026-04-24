/**
 * Generic API call utility (public API, no auth).
 * Supports: GET, POST, PUT, DELETE
 *
 * Options:
 * - httpMethod: "GET" | "POST" | "PUT" | "DELETE"
 * - httpUrl: string
 * - jsonData: object (request body, for POST/PUT/DELETE)
 * - queryParams: object (added to URL as ?key=value)
 * - headers: object (extra headers)
 * - timeoutMs: number (abort request if exceeded)
 */

import { API_BASE_URL } from "../consts";

export async function callApi({
  httpMethod = "GET",
  httpUrl,
  jsonData = null,
  queryParams = null,
  headers = {},
  timeoutMs = 10000,
}) {
  if (!httpUrl) {
    throw new Error("callApi: httpUrl is required");
  }

  const method = httpMethod.toUpperCase();
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    // Build URL with query params if provided
    const url = new URL(httpUrl, API_BASE_URL);
    if (queryParams && typeof queryParams === "object") {
      Object.entries(queryParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const config = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      signal: controller.signal,
    };

    // Attach body for methods that allow it
    if (jsonData && ["POST", "PUT", "DELETE"].includes(method)) {
      config.body = JSON.stringify(jsonData);
    }

    const response = await fetch(url.toString(), config);

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");

    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      return {
        ok: false,
        status: response.status,
        statusText: response.statusText,
        data,
      };
    }

    return {
      ok: true,
      status: response.status,
      statusText: response.statusText,
      data,
    };
  } catch (error) {
    if (error.name === "AbortError") {
      return {
        ok: false,
        status: 408,
        statusText: "Request Timeout",
        data: null,
      };
    }
    return {
      ok: false,
      status: 0,
      statusText: "Network Error",
      data: null,
      error: error.message,
    };
  } finally {
    clearTimeout(timeoutId);
  }
}
