#!/usr/bin/env python3
"""Refresh the published viewer from an original, self-contained Plotly HTML.

Usage: python3 scripts/update_interactive.py /path/to/orientation_anchor_visualization.html
The original file is read only. Uses Python's standard library.
"""
import argparse
import json
from pathlib import Path
import re

def read_original(source):
    text = source.read_text()
    library = next((m.group(1) for m in re.finditer(r'<script\b[^>]*>([\s\S]*?)</script>', text)
                    if 'plotly.js v' in m.group(1)[:200]), None)
    if library is None or 'Plotly.newPlot(' not in text:
        raise ValueError('Expected a self-contained Plotly HTML export with an inline library.')
    remaining = text[text.rfind('Plotly.newPlot(') + len('Plotly.newPlot('):].lstrip()
    args = []
    for _ in range(4):
        value, end = json.JSONDecoder().raw_decode(remaining)
        args.append(value)
        remaining = remaining[end:].lstrip().lstrip(',').lstrip()
    traces, layout, config = args[1:]
    steps = layout['sliders'][0]['steps']
    if len(traces) != 201 or len(steps) != 101:
        raise ValueError('This viewer expects 100 anchors / 201 traces. Review the UI before importing a different dataset.')
    for n, step in enumerate(steps):
        expected = [i < 1 + 2 * n for i in range(201)]
        if step['args'][0]['visible'] != expected:
            raise ValueError('Slider semantics changed; expected cumulative pairs of anchor and projection traces.')
    for i, trace in enumerate(traces):
        trace['visible'] = i < 3
    traces[0]['marker'].update(color='#aab6c5', opacity=0.14, size=1.5)
    layout['sliders'][0].update(active=1, visible=False, currentvalue={'prefix':'Visible anchors: '})
    layout['title'] = {'text':''}
    layout['margin'] = {'l':0,'r':0,'t':10,'b':0}
    layout['paper_bgcolor'] = '#ffffff'
    for axis in ['xaxis','yaxis','zaxis']:
        layout['scene'].setdefault(axis, {}).update(backgroundcolor='#f5f8fc', gridcolor='#dfe6ee', zerolinecolor='#cbd5e1')
    config.update(displaylogo=False, responsive=True, scrollZoom=True)
    return library, {'traces':traces,'layout':layout,'config':config}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    destination = Path(__file__).resolve().parents[1] / 'interactive/orientation_anchor_visualization.html'
    if args.source.resolve() == destination.resolve():
        parser.error('Choose the original export, not the published viewer.')
    library, data = read_original(args.source)
    current = destination.read_text()
    current, library_count = re.subn(r'(<script\b[^>]*>)/\*\*[\s\S]*?plotly\.js v[\s\S]*?</script>',
                                    lambda _: '<script>' + library + '</script>', current, count=1)
    payload = json.dumps(data, separators=(',',':')).replace('</', '<\\/')
    current, data_count = re.subn(r'(<script type="application/json" id="cmrdf-data">)[\s\S]*?</script>',
                                 lambda m: m.group(1) + payload + '</script>', current, count=1)
    if library_count != 1 or data_count != 1:
        raise ValueError('Published viewer template is not recognized; no file was written.')
    destination.write_text(current)
    print('Updated', destination)
    print('Original point coordinates and orientation-support values are preserved. Recapture the preview after browser verification.')

if __name__ == '__main__':
    main()
