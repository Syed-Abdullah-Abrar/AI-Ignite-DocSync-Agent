import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'DocSync 3D Dashboard',
  description: 'Interactive 3D Healthcare Coordination Dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0, overflow: 'hidden' }}>
        {children}
      </body>
    </html>
  )
}
