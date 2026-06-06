/**
 * React entry point.
 *
 * Mounts <App /> into #root. The real implementation should also wire up any
 * global providers (theme, query client, error boundary).
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('AgentStrike dashboard: #root element missing from index.html');
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>
);
