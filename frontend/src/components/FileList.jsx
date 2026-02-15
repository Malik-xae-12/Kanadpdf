/**
 * FileList – sidebar component displaying the list of PDF files.
 * Shows loading skeletons, error state, or the interactive file list.
 */

export default function FileList({
    files,
    loading,
    error,
    selectedFile,
    onSelect,
    onRetry,
}) {
    /* ── Loading state ───────────────────────── */
    if (loading) {
        return (
            <aside className="sidebar" id="file-list-panel">
                <div className="sidebar__header">
                    <p className="sidebar__label">Reports</p>
                    <p className="sidebar__count">Loading…</p>
                </div>
                <div className="sidebar__list">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="skeleton skeleton-item" />
                    ))}
                </div>
            </aside>
        );
    }

    /* ── Error state ─────────────────────────── */
    if (error) {
        return (
            <aside className="sidebar" id="file-list-panel">
                <div className="sidebar__header">
                    <p className="sidebar__label">Reports</p>
                </div>
                <div className="sidebar__error">
                    <p className="sidebar__error-text">{error}</p>
                    <button
                        className="sidebar__error-btn"
                        onClick={onRetry}
                        id="retry-file-list"
                    >
                        Try again
                    </button>
                </div>
            </aside>
        );
    }

    /* ── Normal state ────────────────────────── */
    return (
        <aside className="sidebar" id="file-list-panel">
            <div className="sidebar__header">
                <p className="sidebar__label">Reports</p>
                <p className="sidebar__count">
                    {files.length} file{files.length !== 1 ? "s" : ""}
                </p>
            </div>

            <ul className="sidebar__list">
                {files.length === 0 && (
                    <li style={{ padding: "20px 14px", color: "var(--text-muted)", fontSize: 13 }}>
                        No PDF files found in the reports folder.
                    </li>
                )}

                {files.map((name) => (
                    <li
                        key={name}
                        className={`file-item ${name === selectedFile ? "file-item--active" : ""}`}
                        onClick={() => onSelect(name)}
                        id={`file-${name.replace(/[^a-zA-Z0-9]/g, "-")}`}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => e.key === "Enter" && onSelect(name)}
                    >
                        <div className="file-item__icon">PDF</div>
                        <span className="file-item__name" title={name}>
                            {name}
                        </span>
                    </li>
                ))}
            </ul>
        </aside>
    );
}
