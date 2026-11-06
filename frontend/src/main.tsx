import { StrictMode, startTransition } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './app/App.tsx';
import './styles/index.css';

const root = document.getElementById('root');
if (!root) {
  throw new Error('index.html has no #root element');
}

// As a transition, the first render is split into short tasks, so the phone's main thread is
// never blocked for long while the page builds (Lighthouse's Total Blocking Time, step 4.12)
startTransition(() => {
  createRoot(root).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
});
