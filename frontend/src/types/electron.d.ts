export {}

declare global {
  interface Window {
    electron?: {
      saveTheme: (theme: string) => void
    }
  }
}
