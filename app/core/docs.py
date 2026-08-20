"""SkillBridge AI — Custom Themed Swagger UI & OpenAPI Docs."""

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse

SWAGGER_CUSTOM_CSS = """
/* Dark Theme Customization for SkillBridge AI Swagger UI */
body {
    background-color: #08090a !important;
    color: #e2e8f0 !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}
.swagger-ui {
    color: #cbd5e1 !important;
}
.swagger-ui .topbar {
    background-color: #0d1117 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.swagger-ui .info {
    margin: 30px 0 !important;
}
.swagger-ui .info .title {
    color: #f8fafc !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
.swagger-ui .info .description {
    color: #94a3b8 !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
}
.swagger-ui .scheme-container {
    background-color: #0f172a !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
.swagger-ui .opblock {
    background-color: #0d1117 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    margin: 0 0 16px !important;
}
.swagger-ui .opblock .opblock-summary {
    border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
}
.swagger-ui .opblock .opblock-summary-method {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: monospace !important;
}
.swagger-ui .opblock.opblock-post {
    border-color: rgba(16, 185, 129, 0.3) !important;
    background: rgba(16, 185, 129, 0.03) !important;
}
.swagger-ui .opblock.opblock-post .opblock-summary-method {
    background-color: #10b981 !important;
}
.swagger-ui .opblock.opblock-get {
    border-color: rgba(14, 165, 233, 0.3) !important;
    background: rgba(14, 165, 233, 0.03) !important;
}
.swagger-ui .opblock.opblock-get .opblock-summary-method {
    background-color: #0ea5e9 !important;
}
.swagger-ui .opblock .opblock-summary-path {
    color: #e2e8f0 !important;
    font-family: monospace !important;
    font-size: 14px !important;
}
.swagger-ui .opblock .opblock-summary-description {
    color: #94a3b8 !important;
}
.swagger-ui section.models {
    background-color: #0d1117 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
}
.swagger-ui section.models h4 {
    color: #f1f5f9 !important;
}
.swagger-ui .model-box {
    background-color: #08090a !important;
}
.swagger-ui table thead tr th {
    color: #94a3b8 !important;
    border-bottom: 1px solid #1e293b !important;
}
.swagger-ui table tbody tr td {
    color: #cbd5e1 !important;
}
.swagger-ui input[type=text], .swagger-ui textarea, .swagger-ui select {
    background-color: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
}
.swagger-ui .btn {
    border-radius: 8px !important;
    box-shadow: none !important;
}
.swagger-ui .btn.execute {
    background-color: #38bdf8 !important;
    color: #08090a !important;
    font-weight: 600 !important;
}
"""


def custom_swagger_ui_html(openapi_url: str, title: str) -> HTMLResponse:
    """Return beautifully themed Swagger UI HTML response."""
    html_content = get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    ).body.decode("utf-8")

    # Inject custom dark CSS before </head>
    injected = html_content.replace(
        "</head>",
        f"<style>{SWAGGER_CUSTOM_CSS}</style></head>",
    )
    return HTMLResponse(content=injected)
