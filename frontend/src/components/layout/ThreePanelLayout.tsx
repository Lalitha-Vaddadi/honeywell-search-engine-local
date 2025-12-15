import React from "react";
import type { ReactNode } from "react";
import styles from './ThreePanelLayout.module.css';

interface Props {
  left?: ReactNode;
  center?: ReactNode;
  right?: ReactNode;
  leftWidth?: number;   // default 280
  rightWidth?: number;  // default 320
}

export function ThreePanelLayout({
  left,
  center,
  right,
  leftWidth = 280,
  rightWidth = 320,
}: Props) {
  return (
    <div className={styles.root}>
      <div className={styles.inner}>
        <aside className={styles.left} style={{ width: `${leftWidth}px` }}>
          {left}
        </aside>

        <main className={styles.center}>
          {center}
        </main>

        <aside className={styles.right} style={{ width: `${rightWidth}px` }}>
          {right}
        </aside>
      </div>
    </div>
  );
}

export default ThreePanelLayout;
