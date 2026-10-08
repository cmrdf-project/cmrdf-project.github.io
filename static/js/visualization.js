/* Uses the original Plotly data and the original cumulative visibility masks. */
(() => {
  'use strict';
  const plot = document.getElementById('reachability-plot');
  const slider = document.getElementById('anchor-count');
  const output = document.getElementById('anchor-value');
  const error = document.getElementById('render-error');
  const notify = (type, message) => {
    if (parent !== window) parent.postMessage({type, message}, location.origin);
  };
  const fail = message => {
    error.textContent = message; error.hidden = false;
    slider.disabled = true;
    document.body.dataset.renderState = 'error';
    notify('cmrdf:error', message);
  };
  const canvas = document.createElement('canvas');
  let context;
  try { context = canvas.getContext('webgl2') || canvas.getContext('webgl'); } catch (_) {}
  if (!context) {
    fail('This browser cannot display the 3D view because WebGL is unavailable. Try a browser with hardware acceleration enabled. The figures and paper remain available on the project page.');
    return;
  }
  context.getExtension('WEBGL_lose_context')?.loseContext();
  if (!window.Plotly) { fail('The plotting library could not be loaded. Please reload the page.'); return; }
  const spec = JSON.parse(document.getElementById('cmrdf-data').textContent);
  const steps = spec.layout.sliders[0].steps;
  let requested = 1, applied = 1, updating = false;
  slider.max = String(steps.length - 1);
  const update = async () => {
    if (updating) return;
    updating = true;
    try {
      while (requested !== applied) {
        const count = requested;
        await Plotly.restyle(plot, {visible: steps[count].args[0].visible});
        applied = count;
        output.value = String(count);
        slider.setAttribute('aria-valuetext', `${count} visible anchors`);
        plot.dataset.visibleAnchors = String(count);
      }
    } catch (_) { fail('The 3D view could not be updated. Reload the page to try again.'); }
    finally { updating = false; }
  };
  slider.addEventListener('input', () => { requested = Number(slider.value); update(); });
  document.getElementById('reset-view').addEventListener('click', () => {
    Plotly.relayout(plot, {'scene.camera': {eye:{x:1.25,y:1.25,z:1.25}}});
  });
  Plotly.newPlot(plot, spec.traces, spec.layout, spec.config).then(() => {
    slider.disabled = false;
    plot.dataset.visibleAnchors = '1';
    document.body.dataset.renderState = 'ready';
    plot.querySelectorAll('canvas').forEach(el => el.addEventListener('webglcontextlost', () => {
      fail('The browser lost its 3D graphics context. Reload the view, or try closing other graphics-heavy tabs.');
    }));
    notify('cmrdf:ready');
  }).catch(() => fail('The 3D view could not be rendered. Try another browser or reload the page.'));
})();
