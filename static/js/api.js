/* Tiny fetch wrapper for the JSON API.
 * - sends/receives JSON, keeps the session cookie (same-origin)
 * - on 401 (no/expired session) bounces to the login page
 * - throws Error(message) on failure so callers can show err.message */
window.api = (function () {
  function loginUrl() {
    return (window.CRBS && window.CRBS.urls && window.CRBS.urls.login) || "/";
  }

  async function request(method, path, body) {
    var opts = { method: method, headers: {}, credentials: "same-origin" };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }

    var res = await fetch(path, opts);

    // Session missing/expired — send the user back to login.
    if (res.status === 401 && !window.CRBS_NO_AUTH_REDIRECT) {
      window.location.href = loginUrl();
      throw new Error("Not signed in.");
    }

    var data = null;
    var ct = res.headers.get("Content-Type") || "";
    if (ct.indexOf("application/json") !== -1) data = await res.json();

    if (!res.ok) {
      throw new Error((data && data.error) || ("Request failed (" + res.status + ")"));
    }
    return data;
  }

  return {
    get: function (p) { return request("GET", p); },
    post: function (p, b) { return request("POST", p, b === undefined ? {} : b); },
    put: function (p, b) { return request("PUT", p, b === undefined ? {} : b); },
    del: function (p) { return request("DELETE", p); }
  };
})();
