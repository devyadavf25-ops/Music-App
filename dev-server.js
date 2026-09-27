/**
 * Aura Music Platform — High-Performance Zero-Dependency Dev Server
 * Automatically launches:
 * 1. Web Application on http://localhost:3000 (Serving prototype/ with byte-range and mime support)
 * 2. FastAPI Backend on http://127.0.0.1:8001 (Spawns Uvicorn with auto-reload)
 * 3. Transparent API Proxy from /api/* -> http://127.0.0.1:8001/api/*
 */

const http = require("http");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const PORT = process.env.PORT || 3000;
const BACKEND_PORT = 8001;
const PROTOTYPE_DIR = path.join(__dirname, "prototype");
const BACKEND_DIR = path.join(__dirname, "backend");

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".webmanifest": "application/manifest+json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".wav": "audio/wav",
  ".mp3": "audio/mpeg",
  ".m4a": "audio/mp4",
  ".webm": "audio/webm",
  ".opus": "audio/opus",
  ".ogg": "audio/ogg",
  ".flac": "audio/flac"
};

// Start Python FastAPI Backend
let backendProcess = null;

function startBackend() {
  console.log("\n🚀 Starting Aura FastAPI Backend on port " + BACKEND_PORT + "...");
  const cmd = process.platform === "win32" ? "python" : "python3";
  const args = ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", String(BACKEND_PORT), "--reload"];

  backendProcess = spawn(cmd, args, {
    cwd: BACKEND_DIR,
    stdio: "inherit",
    shell: true
  });

  backendProcess.on("error", (err) => {
    console.warn("⚠️  Could not automatically spawn Python backend: " + err.message);
    console.warn("👉 You can manually run: cd backend && python -m uvicorn app.main:app --port 8001 --reload\n");
  });

  backendProcess.on("exit", (code) => {
    if (code !== 0 && code !== null) {
      console.log("ℹ️  Backend process exited with code " + code);
    }
  });
}

// Proxy API requests to FastAPI
function proxyApiRequest(req, res) {
  const options = {
    hostname: "127.0.0.1",
    port: BACKEND_PORT,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `127.0.0.1:${BACKEND_PORT}`
    }
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res);
  });

  proxyReq.on("error", (err) => {
    // If backend isn't ready yet or down
    res.writeHead(503, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      error: "Backend service starting up or unavailable",
      details: err.message,
      status: "offline_mode_ready"
    }));
  });

  req.pipe(proxyReq);
}

// Static file server with range request support
function serveStaticFile(req, res) {
  let reqPath = req.url.split("?")[0];
  if (reqPath === "/" || reqPath === "") reqPath = "/index.html";

  const filePath = path.join(PROTOTYPE_DIR, reqPath);

  // Prevent directory traversal
  if (!filePath.startsWith(PROTOTYPE_DIR)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fallback to index.html for SPA routing
      const indexPath = path.join(PROTOTYPE_DIR, "index.html");
      fs.readFile(indexPath, (err2, content) => {
        if (err2) {
          res.writeHead(404);
          res.end("Not Found");
        } else {
          res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
          res.end(content);
        }
      });
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || "application/octet-stream";

    // Handle Range Requests for audio/media seeking
    const range = req.headers.range;
    if (range) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stats.size - 1;
      const chunksize = end - start + 1;

      const fileStream = fs.createReadStream(filePath, { start, end });
      res.writeHead(206, {
        "Content-Range": `bytes ${start}-${end}/${stats.size}`,
        "Accept-Ranges": "bytes",
        "Content-Length": chunksize,
        "Content-Type": contentType,
        "Access-Control-Allow-Origin": "*"
      });
      fileStream.pipe(res);
    } else {
      res.writeHead(200, {
        "Content-Length": stats.size,
        "Content-Type": contentType,
        "Accept-Ranges": "bytes",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache, no-store, must-revalidate"
      });
      fs.createReadStream(filePath).pipe(res);
    }
  });
}

const server = http.createServer((req, res) => {
  // CORS Headers for seamless local preview
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, Range, X-Delivered-Bit-Depth, X-Delivered-Sample-Rate");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.url.startsWith("/api/")) {
    proxyApiRequest(req, res);
  } else {
    serveStaticFile(req, res);
  }
});

server.listen(PORT, () => {
  console.log("\n========================================================");
  console.log("   🎵 AURA MUSIC PLATFORM — NEXT-GEN DEV ENVIRONMENT");
  console.log("========================================================");
  console.log(`   🌐 Web Application:      http://localhost:${PORT}`);
  console.log(`   ⚡ FastAPI Backend API:  http://127.0.0.1:${BACKEND_PORT}/docs`);
  console.log(`   💾 Offline Music Vault:  Enabled (IndexedDB + Blob Cache)`);
  console.log(`   🎧 YouTube Audio Proxy:  Active with 206 Range Streaming`);
  console.log("========================================================\n");
  startBackend();
});

// Clean up child process on exit
process.on("SIGINT", () => {
  console.log("\n🛑 Stopping servers...");
  if (backendProcess) backendProcess.kill();
  server.close(() => process.exit(0));
});

process.on("SIGTERM", () => {
  if (backendProcess) backendProcess.kill();
  server.close(() => process.exit(0));
});
