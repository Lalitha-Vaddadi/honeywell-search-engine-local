import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { HiSearch } from 'react-icons/hi';
import { searchApi } from '@/api';
import { Loader } from '@/components/common';
import { CONFIDENCE_THRESHOLDS } from '@/utils/constants';
import type { SearchResult } from '@/types';
import styles from '@/pages/SearchPage/SearchPage.module.css';

export function RightPanelSearchChat({
  openDocument,
}: {
  openDocument?: (id: string, page?: number) => void;
}) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);

  const [results, setResults] = useState<SearchResult[]>([]);
  const [searchTime, setSearchTime] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const runSearch = async (text: string) => {
    if (!text.trim()) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setIsLoading(true);
    setHasSearched(true);

    try {
      const res = await searchApi.search({ query: text.trim(), limit: 20 });
      setResults(res.data.results);
      setSearchTime(res.data.searchTime);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runSearch(initialQuery);
  }, [initialQuery]);

  const getScoreClass = (score: number) => {
    if (score >= CONFIDENCE_THRESHOLDS.HIGH) return styles.high;
    if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return styles.medium;
    return styles.low;
  };

  const handleSearchSubmit = () => {
    if (!query.trim()) return;
    // update URL
    navigate(`/dashboard?q=${encodeURIComponent(query)}`);
    runSearch(query);
  };

  return (
    <div style={{ padding: 16, height: "100%", display: "flex", flexDirection: "column" }}>

      {/* Top label */}
      <h3 style={{ marginBottom: 16 }}>Search</h3>

      {/* MAIN SCROLLABLE RESULTS AREA */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {isLoading && <Loader text="Searching..." />}

        {!isLoading && hasSearched && (
          <>
            <div style={{ marginBottom: 12, fontSize: 13, color: "var(--color-text-secondary)" }}>
              {results.length} result(s)
              {searchTime !== null ? ` in ${searchTime.toFixed(3)}s` : ""}
            </div>

            {results.length === 0 ? (
              <div style={{ textAlign: "center", padding: 20 }}>
                <HiSearch size={36} />
                <p>No results</p>
              </div>
            ) : (
              <div>
                {results.map((r, idx) => (
                  <div
                    key={`${r.documentId}-${r.pageNumber}-${idx}`}
                    className={styles.resultCard}
                    onClick={() => {
                      openDocument?.(r.documentId, r.pageNumber);
                    }}
                    style={{ cursor: "pointer" }}
                  >
                    <div className={styles.resultContent}>
                      <div className={styles.resultHeader}>
                        <span className={styles.documentName}>{r.documentName}</span>
                        <span className={styles.pageNumber}>Page {r.pageNumber}</span>
                      </div>
                      <p
                        className={styles.snippet}
                        dangerouslySetInnerHTML={{ __html: r.snippet }}
                      />
                    </div>

                    <div className={styles.confidenceScore}>
                      <span
                        className={`${styles.scoreValue} ${getScoreClass(r.confidenceScore)}`}
                      >
                        {Math.round(r.confidenceScore)}%
                      </span>
                      <span className={styles.scoreLabel}>match</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* SEARCH INPUT AT BOTTOM */}
      <div
        style={{
          paddingTop: 12,
          borderTop: "1px solid var(--color-border)",
          display: "flex",
          gap: 8,
          alignItems: "center",
          marginTop: 12,
        }}
      >
        <input
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearchSubmit()}
          style={{
            flex: 1,
            padding: "8px 10px",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            fontSize: 14,
          }}
        />
        <button
          onClick={handleSearchSubmit}
          style={{
            background: "var(--color-primary)",
            border: "none",
            color: "white",
            padding: "8px 10px",
            borderRadius: "6px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <HiSearch size={18} />
        </button>
      </div>
    </div>
  );
}

export default RightPanelSearchChat;
