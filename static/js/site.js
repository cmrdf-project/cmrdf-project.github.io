/* Native, dependency-free controls for the academic page. */
(() => {
  'use strict';
  const copy = document.querySelector('[data-copy-citation]');
  if (copy) copy.addEventListener('click', async () => {
    const code = document.getElementById('bibtex-code');
    const status = document.getElementById('copy-status');
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(code.textContent);
      copy.textContent = 'Copied';
      status.textContent = 'BibTeX copied to clipboard.';
      setTimeout(() => { copy.textContent = 'Copy BibTeX'; }, 2200);
    } catch (_) {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges(); selection.addRange(range);
      status.textContent = 'Citation selected. Press Ctrl+C (or ⌘C) to copy.';
    }
  });

  document.querySelectorAll('[data-demo]').forEach(card => {
    const stage = card.querySelector('.demo-stage');
    const poster = card.querySelector('.demo-poster');
    const status = card.querySelector('.demo-status');
    const error = card.querySelector('.demo-error');
    const launch = card.querySelector('[data-launch-demo]');
    const retry = card.querySelector('[data-retry-demo]');
    let frame, timer;
    const fail = message => {
      clearTimeout(timer);
      stage.setAttribute('aria-busy', 'false');
      status.hidden = true;
      if (frame) { frame.remove(); frame = null; }
      error.querySelector('[data-error-message]').textContent = message;
      error.hidden = false;
      retry.hidden = false;
    };
    const start = () => {
      clearTimeout(timer);
      if (frame) frame.remove();
      if (poster) poster.hidden = true;
      error.hidden = true;
      status.hidden = false;
      status.textContent = 'Loading the 3D visualization…';
      stage.setAttribute('aria-busy', 'true');
      frame = document.createElement('iframe');
      frame.className = 'demo-frame';
      frame.title = 'CMRDF position anchors and orientation support';
      frame.setAttribute('allow', 'fullscreen');
      frame.style.visibility = 'hidden';
      frame.src = card.dataset.demoSrc;
      frame.addEventListener('error', () => fail('The visualization could not be loaded. Check your connection and try again.'));
      frame.addEventListener('load', () => {
        try {
          if (!frame.contentDocument.querySelector('[data-cmrdf-visualization]')) {
            fail('The visualization file could not be found. You can retry or open the dedicated page.');
          }
        } catch (_) {
          fail('The visualization could not be opened. Please try the dedicated page.');
        }
      });
      stage.appendChild(frame);
      timer = setTimeout(() => fail('Loading is taking longer than expected. Please check your connection, then try again or open the dedicated page.'), 60000);
    };
    window.addEventListener('message', event => {
      if (!frame || event.origin !== location.origin || event.source !== frame.contentWindow) return;
      if (event.data?.type === 'cmrdf:ready') {
        clearTimeout(timer); status.hidden = true;
        stage.setAttribute('aria-busy', 'false'); frame.style.visibility = 'visible';
      } else if (event.data?.type === 'cmrdf:error') {
        fail(event.data.message || 'The 3D view could not be rendered in this browser.');
      }
    });
    if (launch) launch.addEventListener('click', start);
    retry.addEventListener('click', start);
    if (card.dataset.autoload === 'true') start();
  });
})();
