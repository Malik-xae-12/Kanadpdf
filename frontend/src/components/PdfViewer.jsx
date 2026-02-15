/**
 * PdfViewer – right-side panel that displays the selected PDF,
 * a loading spinner, an error banner, or an empty-state prompt.
 */

export default function PdfViewer({
    filename,
    pdfUrl,
    loading,
    error,
    onRetry,
}) {
    /* ── Loading ─────────────────────────────── */
    if (loading) {
        return (
            <section className="viewer" id="pdf-viewer-panel">
                <div className="spinner-wrapper">
                    <div className="spinner" />
                    <span className="spinner-text">Loading {filename}…</span>
                </div>
            </section>
        );
    }

    /* ── Error ───────────────────────────────── */
    if (error) {
        return (
            <section className="viewer" id="pdf-viewer-panel">
                <div className="error-banner">
                    <span className="error-banner__icon">⚠️</span>
                    <div>
                        <p className="error-banner__title">Failed to load PDF</p>
                        <p className="error-banner__message">{error}</p>
                        <button
                            className="error-banner__retry"
                            onClick={onRetry}
                            id="retry-pdf"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </section>
        );
    }

    /* ── PDF loaded ──────────────────────────── */
    if (pdfUrl) {
        return (
            <section className="viewer" id="pdf-viewer-panel">
                <iframe
                    className="viewer__iframe"
                    src={pdfUrl}
                    title={`Viewing ${filename}`}
                    id="pdf-iframe"
                />
            </section>
        );
    }

    /* ── Empty state ─────────────────────────── */
    return (
        <section className="viewer" id="pdf-viewer-panel">
            <div className="viewer__empty">
                <div className="viewer__empty-icon">📄</div>
                <p className="viewer__empty-title">No file selected</p>
                <p className="viewer__empty-subtitle">
                    Choose a PDF report from the sidebar to preview it here.
                </p>
            </div>
        </section>
    );
}
