import React from "react";
import type { ReactNode } from "react";
// import styles from "./ThreePanelLayout.module.css";

interface Props {
  left?: ReactNode;
  center?: ReactNode;
  right?: ReactNode;
  leftWidth?: number;
  rightWidth?: number;
}

export function ThreePanelLayout({
  left,
  center,
  right,
  leftWidth = 280,
  rightWidth = 320,
}: Props) {
  return (
    <div
      style={{
        height: "100%",
        display: "flex",
        overflow: "hidden",
      }}
    >
      <aside style={{ width: leftWidth, overflowY: "auto" }}>
        {left}
      </aside>

      <main
        style={{
          flex: 1,
          overflow: "hidden",
        }}
      >
        {center}
      </main>

      <aside style={{ width: rightWidth, overflowY: "auto" }}>
        {right}
      </aside>
    </div>
  );
}

export default ThreePanelLayout;
