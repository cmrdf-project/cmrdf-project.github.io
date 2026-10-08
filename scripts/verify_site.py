#!/usr/bin/env python3
"""Browser acceptance checks. Requires Playwright + Chromium; preview server must be running."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8765')
    parser.add_argument('--output-dir', type=Path, default=Path('/tmp/cmrdf-site-check'))
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    results = []
    def passed(name, **details):
        results.append({'check':name,'passed':True,**details})
        print('PASS', name, flush=True)
    def no_overflow(page):
        return page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        ctx = browser.new_context(viewport={'width':1440,'height':1000})
        page = ctx.new_page()
        failures, errors, requests = [], [], []
        page.on('response', lambda response: failures.append((response.status,response.url)) if response.status >= 400 else None)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        page.goto(base+'/', wait_until='networkidle')
        assert page.locator('h1').inner_text() == 'CMRDF: Morphology-Conditioned Reachability Fields for Task-Space Robot Policy Transfer'
        assert page.locator('iframe').count() == 0
        assert not any('orientation_anchor_visualization' in u for u in requests)
        passed('Homepage does not load the interactive HTML before clicking')
        assert no_overflow(page)
        assert page.locator('img').evaluate_all('(images)=>images.every(i=>i.complete && i.naturalWidth>0)')
        page.screenshot(path=str(out/'desktop.png'), full_page=True)
        page.screenshot(path=str(out/'desktop-first-screen.png'))
        passed('Desktop layout and images at 1440px')
        ctx.grant_permissions(['clipboard-read','clipboard-write'], origin=base)
        page.get_by_role('button', name='Copy BibTeX', exact=True).click()
        page.wait_for_function('document.getElementById("copy-status").textContent.includes("copied")')
        assert page.evaluate('navigator.clipboard.readText()') == page.locator('#bibtex-code').text_content()
        passed('BibTeX copy')
        page.get_by_role('button', name='Explore in 3D').click()
        page.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"', timeout=60000)
        frame = page.frames[1]
        frame.wait_for_selector('body[data-render-state="ready"]')
        count = frame.locator('#reachability-plot').evaluate('(el)=>el.data.filter(t=>t.visible).length')
        assert count == 3
        passed('Click-to-load renders initial one-anchor state', visible_traces=count)
        slider = frame.locator('#anchor-count')
        for n in [0,1,50,100]:
            # Standard input event, followed by an assertion on rendered Plotly state.
            slider.evaluate('(el,n)=>{el.value=n;el.dispatchEvent(new Event("input",{bubbles:true}));}', n)
            frame.wait_for_function('(n)=>document.querySelector("#reachability-plot").dataset.visibleAnchors===String(n)', arg=n, timeout=60000)
            actual = frame.locator('#reachability-plot').evaluate('(el)=>el.data.filter(t=>t.visible).length')
            assert actual == 1 + 2*n, (n,actual)
            assert frame.locator('#anchor-value').text_content() == str(n)
            passed(f'Anchor count {n}', visible_traces=actual)
        slider.press('Home'); slider.press('ArrowRight')
        frame.wait_for_function('document.querySelector("#reachability-plot").dataset.visibleAnchors==="1"', timeout=60000)
        passed('Slider keyboard operation')
        camera = frame.locator('#reachability-plot').evaluate('(el)=>JSON.stringify(el._fullLayout.scene.camera)')
        canvas = frame.locator('#reachability-plot canvas').first
        box = canvas.bounding_box()
        page.mouse.move(box['x']+box['width']*.48, box['y']+box['height']*.48)
        page.mouse.down()
        page.mouse.move(box['x']+box['width']*.63, box['y']+box['height']*.60, steps=12)
        page.mouse.up()
        frame.wait_for_function('(old)=>JSON.stringify(document.getElementById("reachability-plot")._fullLayout.scene.camera)!==old', arg=camera)
        before_zoom = frame.locator('#reachability-plot').evaluate('(el)=>JSON.stringify(el._fullLayout.scene.camera)')
        page.mouse.wheel(0, -160)
        frame.wait_for_function('(old)=>JSON.stringify(document.getElementById("reachability-plot")._fullLayout.scene.camera)!==old', arg=before_zoom)
        frame.get_by_role('button',name='Reset view').click()
        frame.wait_for_function('document.getElementById("reachability-plot")._fullLayout.scene.camera.eye.x===1.25')
        passed('3D drag, wheel zoom and reset')
        page.locator('#demo').screenshot(path=str(out/'interactive-desktop.png'))
        assert not failures, failures
        assert not errors, errors
        passed('No page errors or failing resource requests')
        for path,content_type in [('/interactive/','text/html'),('/static/pdfs/cmrdf.pdf','application/pdf')]:
            response = ctx.request.get(base+path)
            assert response.status == 200
            assert content_type in response.headers.get('content-type','')
        passed('Standalone and PDF routes')
        page.goto(base+'/interactive/', wait_until='domcontentloaded')
        page.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"', timeout=60000)
        page.reload(wait_until='domcontentloaded')
        page.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"', timeout=60000)
        passed('Dedicated page loads automatically and survives refresh')
        ctx.close()

        mobile = browser.new_context(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True, device_scale_factor=1)
        mp = mobile.new_page(); mp.goto(base+'/',wait_until='networkidle')
        assert no_overflow(mp)
        mp.screenshot(path=str(out/'mobile.png'),full_page=True)
        mp.screenshot(path=str(out/'mobile-first-screen.png'))
        mp.get_by_role('button', name='Explore in 3D').click()
        mp.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"', timeout=60000)
        assert no_overflow(mp)
        assert mp.frames[1].evaluate('document.documentElement.scrollWidth <= innerWidth')
        mp.locator('#demo').screenshot(path=str(out/'interactive-mobile.png'))
        passed('Mobile layout and embedded interaction at 390px')
        mp.goto(base+'/interactive/')
        mp.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"', timeout=60000)
        assert no_overflow(mp)
        mp.screenshot(path=str(out/'dedicated-mobile.png'),full_page=True)
        passed('Dedicated mobile view')
        mobile.close()

        failure_ctx = browser.new_context()
        fp = failure_ctx.new_page()
        fp.route('**/interactive/orientation_anchor_visualization.html',lambda route:route.fulfill(status=404,body='Not found',content_type='text/html'))
        fp.goto(base+'/'); fp.get_by_role('button',name='Explore in 3D').click()
        fp.locator('.demo-error').wait_for(state='visible')
        assert 'could not be found' in fp.locator('[data-error-message]').inner_text()
        fp.unroute('**/interactive/orientation_anchor_visualization.html')
        fp.get_by_role('button',name='Try again').click()
        fp.wait_for_function('document.querySelector("iframe")?.style.visibility === "visible"',timeout=60000)
        passed('Missing visualization shows an error; retry recovers')
        failure_ctx.close()

        no_gl = browser.new_context()
        no_gl.add_init_script('''const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type.includes('webgl')?null:original.call(this,type,...args)};''')
        gp = no_gl.new_page(); gp.goto(base+'/interactive/')
        gp.locator('.demo-error').wait_for(state='visible',timeout=60000)
        assert 'WebGL is unavailable' in gp.locator('[data-error-message]').inner_text()
        passed('WebGL unavailable is reported clearly')
        no_gl.close()
        browser.close()
    (out/'report.json').write_text(json.dumps({'base_url':base,'results':results},indent=2)+'\n')
    print(f'{len(results)} acceptance checks passed. Screenshots and report: {out}')

if __name__ == '__main__':
    main()
