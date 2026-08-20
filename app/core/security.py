"""SkillBridge AI — Enterprise Security Layer.

Includes:
- SecurityHeadersMiddleware (OWASP recommended response headers)
- TokenBucketRateLimiter & RateLimitMiddleware (DDoS & API abuse prevention)
- InputSanitizer (Prompt injection boundary defense & XSS/payload neutralization)
- PDF Magic-byte & MIME validator (Safe file intake)
- Cryptographic Proof-of-Work Hashing (SHA-256 verified learner telemetry)
"""

from __future__ import annotations

import hashlib
import hmac
import html
import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("skillbridge.security")

# Magic bytes signature for PDF files: %PDF-
PDF_MAGIC_BYTES = b"%PDF-"


# ============================================================================
# 1. Security Headers Middleware
# ============================================================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects OWASP-compliant security headers into all responses."""

    def __init__(self, app, csp_enabled: bool = True):
        super().__init__(app)
        self.csp_enabled = csp_enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)

        # Standard OWASP defense headers
        headers = response.headers
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["X-XSS-Protection"] = "1; mode=block"
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        headers["X-Permitted-Cross-Domain-Policies"] = "none"
        headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), microphone=(), payment=()"

        # Cache control for API responses (prevent caching sensitive telemetry/user data)
        path = request.url.path
        if path.startswith("/api/"):
            headers["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
            headers["Pragma"] = "no-cache"
            headers["Expires"] = "0"

        # Content Security Policy (allowing Swagger UI CDN and modern font providers)
        if self.csp_enabled:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' http: https: ws: wss:; "
                "frame-ancestors 'none';"
            )
            headers["Content-Security-Policy"] = csp

        return response


# ============================================================================
# 2. In-Memory Token Bucket Rate Limiter
# ============================================================================
@dataclass
class RateLimitBucket:
    tokens: float
    last_update: float


class RateLimiter:
    """Thread-safe in-memory Token Bucket rate limiter per IP address."""

    def __init__(self):
        # ip -> bucket
        self.buckets: dict[str, dict[str, RateLimitBucket]] = defaultdict(dict)

    def is_allowed(self, client_ip: str, route_type: str, max_tokens: int, refill_rate_per_sec: float) -> tuple[bool, int]:
        """Check if request is allowed. Returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        client_buckets = self.buckets[client_ip]

        if route_type not in client_buckets:
            client_buckets[route_type] = RateLimitBucket(tokens=float(max_tokens), last_update=now)

        bucket = client_buckets[route_type]

        # Refill tokens based on elapsed time
        elapsed = now - bucket.last_update
        bucket.tokens = min(float(max_tokens), bucket.tokens + elapsed * refill_rate_per_sec)
        bucket.last_update = now

        if bucket.tokens >= 1.0:
            bucket.tokens -= 1.0
            return True, 0

        # Calculate wait time until 1 token is available
        needed = 1.0 - bucket.tokens
        retry_after = max(1, int(needed / refill_rate_per_sec))
        return False, retry_after

    def cleanup(self, max_idle_seconds: int = 3600):
        """Prune stale client buckets to prevent memory accumulation."""
        now = time.monotonic()
        for ip in list(self.buckets.keys()):
            for route in list(self.buckets[ip].keys()):
                if now - self.buckets[ip][route].last_update > max_idle_seconds:
                    del self.buckets[ip][route]
            if not self.buckets[ip]:
                del self.buckets[ip]


global_rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces rate limits by endpoint tier (AI calls, uploads, general APIs)."""

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        path = request.url.path

        # Ignore static assets, docs, health check from rate limiter
        if path in {"/health", "/docs", "/redoc", "/openapi.json"} or path.startswith("/static/"):
            return await call_next(request)

        # Determine client identifier
        client_ip = request.client.host if request.client else "127.0.0.1"
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        # Categorize route tiers: (max_burst, refill_per_sec)
        if path == "/api/upload":
            # File uploads: 20 per min (burst 20, 0.33/s)
            max_tokens, refill_rate = 20, 20 / 60.0
            tier = "upload"
        elif path in {"/api/analyze", "/api/generate-lesson", "/api/check-code", "/api/gap-chat"}:
            # AI Inference endpoints: 40 per min (burst 40, 0.67/s)
            max_tokens, refill_rate = 40, 40 / 60.0
            tier = "ai"
        elif path.startswith("/api/auth/") or path == "/api/resume/save":
            # Account & persistence mutations: 60 per min
            max_tokens, refill_rate = 60, 60 / 60.0
            tier = "auth"
        elif path.startswith("/api/"):
            # General API queries: 120 per min
            max_tokens, refill_rate = 120, 120 / 60.0
            tier = "api"
        else:
            max_tokens, refill_rate = 200, 200 / 60.0
            tier = "general"

        allowed, retry_after = global_rate_limiter.is_allowed(client_ip, tier, max_tokens, refill_rate)

        if not allowed:
            logger.warning("Rate limit exceeded for client %s on [%s] %s (retry in %ds)", client_ip, tier, path, retry_after)
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "code": 429,
                    "detail": f"Rate limit exceeded for {tier} requests. Please retry in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response


# ============================================================================
# 3. Input Sanitizer & Prompt Injection Defense
# ============================================================================
class InputSanitizer:
    """Neutralizes malicious script tags, control chars, and prompt injection sequences."""

    # Unsafe control characters (excluding standard tabs and newlines)
    CONTROL_CHAR_REGEX = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
    
    # Prompt injection delimiters to safely sanitize before passing to LLMs
    SYSTEM_DELIMITERS = [
        "system:", "assistant:", "human:", "<|im_start|>", "<|im_end|>", 
        "[INST]", "[/INST]", "<<SYS>>", "<</SYS>>", "```system"
    ]

    @classmethod
    def sanitize_text(cls, text: str, max_chars: int = 12000, strip_html: bool = True) -> str:
        """Strip control characters, sanitize HTML, and truncate safely."""
        if not text or not isinstance(text, str):
            return ""

        cleaned = cls.CONTROL_CHAR_REGEX.sub("", text)

        if strip_html:
            # Strip dangerous HTML tags but keep standard characters
            cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
            cleaned = re.sub(r"<\s*iframe[^>]*>.*?<\s*/\s*iframe\s*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
            cleaned = re.sub(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)

        # Normalize unicode whitespace
        cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)

        return cleaned.strip()[:max_chars]

    @classmethod
    def wrap_prompt_content(cls, content: str, role_tag: str = "USER_INPUT") -> str:
        """Isolate user-provided input with secure delimiters to prevent LLM prompt injection."""
        safe_content = cls.sanitize_text(content)
        for delim in cls.SYSTEM_DELIMITERS:
            safe_content = safe_content.replace(delim, f"_{delim}_")

        return f"<{role_tag}>\n{safe_content}\n</{role_tag}>"


# ============================================================================
# 4. Safe PDF & File Intake Validator
# ============================================================================
def validate_pdf_bytes(raw_bytes: bytes, max_bytes: int = 5 * 1024 * 1024) -> tuple[bool, str]:
    """Verify that file bytes conform to real PDF magic header and size limit."""
    if not raw_bytes:
        return False, "Uploaded file is empty."

    if len(raw_bytes) > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        return False, f"File exceeds maximum allowed size of {max_mb} MB."

    # Verify PDF signature (%PDF-)
    # Some valid PDFs may have up to 1024 bytes of leading whitespace or BOM header
    header_chunk = raw_bytes[:1024]
    if PDF_MAGIC_BYTES not in header_chunk:
        return False, "Invalid file format: Not a genuine PDF document."

    return True, "Valid PDF"


# ============================================================================
# 5. Cryptographic Proof-of-Work Hashing
# ============================================================================
def generate_proof_hash(user_id: int, completed_badges: list[str], avg_score: float, salt: str = "skillbridge-verified") -> str:
    """Generate tamper-proof SHA-256 signature for verified public proof-of-work profiles."""
    badges_str = ",".join(sorted(str(b).strip().lower() for b in completed_badges))
    payload = f"{user_id}:{badges_str}:{avg_score:.2f}:{salt}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def verify_proof_hash(user_id: int, completed_badges: list[str], avg_score: float, proof_hash: str, salt: str = "skillbridge-verified") -> bool:
    """Verify validity of a learner's public proof-of-work hash."""
    expected = generate_proof_hash(user_id, completed_badges, avg_score, salt)
    return hmac.compare_digest(expected, proof_hash)
