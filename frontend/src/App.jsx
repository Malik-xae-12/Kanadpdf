import { useState, useEffect, useCallback } from "react";
import FileList from "./components/FileList.jsx";
import PdfViewer from "./components/PdfViewer.jsx";
import api from "./api.js";

export default function App() {
    /* ── State ───────────────────────────────── */
    const [files, setFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const [pdfUrl, setPdfUrl] = useState(null);

    const [filesLoading, setFilesLoading] = useState(true);
    const [filesError, setFilesError] = useState(null);

    const [pdfLoading, setPdfLoading] = useState(false);
    const [pdfError, setPdfError] = useState(null);

    /* ── Fetch file list ─────────────────────── */
    const fetchFiles = useCallback(async () => {
        setFilesLoading(true);
        setFilesError(null);
        try {
            const { data } = await api.get("/files");
            setFiles(data);
        } catch (err) {
            setFilesError(err.message);
        } finally {
            setFilesLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchFiles();
    }, [fetchFiles]);

    /* ── Select & load a PDF ─────────────────── */
    const handleSelectFile = useCallback(
        async (filename) => {
            if (filename === selectedFile) return;

            // Revoke previous blob URL to free memory
            if (pdfUrl) URL.revokeObjectURL(pdfUrl);

            setSelectedFile(filename);
            setPdfUrl(null);
            setPdfError(null);
            setPdfLoading(true);

            try {
                const { data } = await api.get(`/files/${encodeURIComponent(filename)}`, {
                    responseType: "blob",
                });
                const url = URL.createObjectURL(data);
                setPdfUrl(url);
            } catch (err) {
                setPdfError(err.message);
            } finally {
                setPdfLoading(false);
            }
        },
        [selectedFile, pdfUrl]
    );

    /* ── Clean up blob URL on unmount ────────── */
    useEffect(() => {
        return () => {
            if (pdfUrl) URL.revokeObjectURL(pdfUrl);
        };
    }, [pdfUrl]);

    /* ── Render ──────────────────────────────── */
    return (
        <>
            {/* Header */}
            <header className="header">
                <div className="header__logo">OL</div>
                <h1 className="header__title">kanad PDF Viewer</h1>
                <span className="header__badge">Fabric • Lakehouse</span>
            </header>

            {/* Main content */}
            <main className="main">
                <FileList
                    files={files}
                    loading={filesLoading}
                    error={filesError}
                    selectedFile={selectedFile}
                    onSelect={handleSelectFile}
                    onRetry={fetchFiles}
                />

                <PdfViewer
                    filename={selectedFile}
                    pdfUrl={pdfUrl}
                    loading={pdfLoading}
                    error={pdfError}
                    onRetry={() => selectedFile && handleSelectFile(selectedFile)}
                />
            </main>
        </>
    );
}
