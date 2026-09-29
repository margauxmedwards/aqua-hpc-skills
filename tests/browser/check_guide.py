"""Optional browser check: install playwright, then run with a local Chrome binary.

python3 tests/browser/check_guide.py
Set CHROME_BIN to override the discovered browser. No HPC/network actions occur.
"""
import os
from pathlib import Path
import shutil
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def assert_text_contrast(page):
    failures = page.evaluate("""() => {
      const rgb = value => (value.match(/[\\d.]+/g) || []).map(Number);
      const luminance = channels => channels.slice(0, 3).map(c => {
        c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
      }).reduce((sum, c, i) => sum + c * [0.2126, 0.7152, 0.0722][i], 0);
      const background = element => {
        for (let node = element; node; node = node.parentElement) {
          const color = rgb(getComputedStyle(node).backgroundColor);
          if (color.length === 3 || color[3] === 1) return color;
        }
        return [255, 255, 255];
      };
      const failures = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const node = walker.currentNode, element = node.parentElement;
        if (!node.textContent.trim() || !element || element.closest('script, style, noscript, .sr-only')) continue;
        const style = getComputedStyle(element);
        if (!element.getClientRects().length || style.visibility !== 'visible') continue;
        const fg = luminance(rgb(style.color)), bg = luminance(background(element));
        const ratio = (Math.max(fg, bg) + .05) / (Math.min(fg, bg) + .05);
        const large = parseFloat(style.fontSize) >= 24 || (parseFloat(style.fontSize) >= 18.66 && Number(style.fontWeight) >= 700);
        if (ratio < (large ? 3 : 4.5)) failures.push({text:node.textContent.trim().slice(0,70),ratio});
      }
      return failures;
    }""")
    assert not failures, f'Text contrast failures: {failures}'


def main():
    browser_path = os.environ.get('CHROME_BIN') or shutil.which('google-chrome') or shutil.which('chromium')
    if not browser_path:
        raise SystemExit('Set CHROME_BIN to a local Chrome/Chromium executable')
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=browser_path, headless=True,
                                   args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        requests = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        pages = [('index.html', 'Aqua field guide'), ('first-job.html', 'Your first Aqua job'),
                 ('rpid.html', 'RPID requirement'), ('walltime.html', 'Walltime calculator'),
                 ('mount.html', 'Mount Aqua'), ('ros.html', 'ROS on Aqua'), ('notify.html', 'Notifications'), ('agents.html', 'AI agent guide')]
        for name, title in pages:
            page.goto((ROOT/'docs'/name).as_uri())
            assert page.title().startswith(title)
            assert page.locator('h1').count() == 1
            for scheme in ['light', 'dark']:
                page.emulate_media(color_scheme=scheme)
                page.locator('details').evaluate_all('(elements) => elements.forEach(el => el.open = true)')
                assert_text_contrast(page)
                page.locator('details').evaluate_all('(elements) => elements.forEach(el => el.open = false)')
                assert 'light' in page.locator('html').evaluate('(el) => getComputedStyle(el).colorScheme')
            page.emulate_media(color_scheme='light')
            for width in [1440, 768, 390]:
                page.set_viewport_size({'width': width, 'height': 1000})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}px on {name}'
            page.set_viewport_size({'width': 1440, 'height': 1000})
            current = page.locator('.site-nav a[aria-current="page"]')
            assert current.count() == 1 and current.get_attribute('href') == name, name
        # Agent guide (agents.html) is loaded now.
        assert page.locator('a[href="first-job.html"]').count() >= 1
        assert page.locator('a[href="https://github.com/margauxmedwards/ai4coding"]').count() == 1
        page.get_by_role('button', name='Claude Code', exact=True).click()
        assert '--agent claude' in page.locator('#install-command').inner_text()
        assert page.locator('#first-prompt').inner_text().startswith('/aqua-hpc')
        page.get_by_role('button', name='Copilot', exact=True).click()
        assert '.github/skills' in page.locator('#agent-location').inner_text()
        assert page.locator('#first-prompt').inner_text().startswith('Use the aqua-hpc skill')
        page.get_by_role('button', name='Codex', exact=True).click()
        assert page.locator('[data-agent][aria-pressed="true"]').count() == 1
        assert page.locator('#first-prompt').inner_text().startswith('$aqua-hpc')

        page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async text=>{window.copiedText=text;}}})")
        page.locator('[data-copy="install-command"]').click()
        page.wait_for_function('window.copiedText !== undefined')
        assert '--agent codex' in page.evaluate('window.copiedText')
        page.locator('details').evaluate_all('(elements) => elements.forEach(el => el.open = false)')
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        assert page.locator('details:not([open])').count() == 0
        page.evaluate("window.dispatchEvent(new Event('afterprint'))")
        assert page.locator('details[open]').count() == 0
        page.evaluate('window.scrollTo(0,0)')
        screenshots = Path(tempfile.gettempdir())/'aqua-guide-screenshots'
        screenshots.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshots/'desktop.png'))
        page.set_viewport_size({'width': 390, 'height': 844})
        page.screenshot(path=str(screenshots/'mobile.png'))
        page.set_viewport_size({'width': 1440, 'height': 1000})

        # Home page: every guide is one click away.
        page.goto((ROOT/'docs/index.html').as_uri())
        for href in ['first-job.html', 'agents.html', 'rpid.html', 'walltime.html', 'mount.html', 'notify.html', 'ros.html']:
            assert page.locator(f'a.link-card[href="{href}"]').count() == 1, href
        page.screenshot(path=str(screenshots/'home-desktop.png'))
        page.locator('a.link-card[href="rpid.html"]').click()
        assert page.url.endswith('rpid.html')

        # RPID page (rpid.html): local helper.
        # Synthetic format-valid identifier stays local and is never submitted.
        page.locator('#rpid-value').fill('ABCDEF1234')
        page.get_by_role('button', name='Build commands', exact=True).click()
        assert 'not accepted' in page.locator('#rpid-status').inner_text()
        assert page.locator('#rpid-generated-box').is_hidden()
        page.locator('#rpid-value').fill('TESTXX0000')
        page.get_by_role('button', name='Build commands', exact=True).click()
        assert '#PBS -P TESTXX0000' in page.locator('#rpid-generated').inner_text()
        assert 'Confirm project authorization' in page.locator('#rpid-status').inner_text()
        page.locator('#rpid-value').fill('bad')
        assert page.locator('#rpid-generated-box').is_hidden(), 'Stale valid command must disappear'
        assert not page.locator('#rpid-value').evaluate('(el) => el.checkValidity()')
        page.reload()
        assert page.locator('#rpid-value').input_value() == ''

        # Walltime page (walltime.html): local calculator.
        page.goto((ROOT/'docs/walltime.html').as_uri())
        page.get_by_role('button', name='Calculate walltime', exact=True).click()
        assert '01:15:00' in page.locator('#walltime-result').inner_text()
        assert 'Fits the supplied limit' in page.locator('#walltime-result').inner_text()
        page.locator('#limit').fill('1')
        page.get_by_role('button', name='Calculate walltime', exact=True).click()
        assert 'Exceeds the supplied limit' in page.locator('#walltime-result').inner_text()
        page.locator('#records').fill('0')
        assert not page.locator('#records').evaluate('(el) => el.checkValidity()')

        # Blocked-clipboard fallback without OS access.
        page.goto((ROOT/'docs/rpid.html').as_uri())
        page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async ()=>{throw Error('blocked');}}})")
        page.locator('[data-copy="rpid-command"]').click()
        page.wait_for_function("document.getElementById('copy-status').textContent.includes('Text selected')")
        assert 'qsub -P' in page.evaluate('window.getSelection().toString()')
        assert not errors, errors
        assert not any(url.startswith(('http:', 'https:')) for url in requests), requests
        no_js = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        plain = no_js.new_page()
        for name, form in [('rpid.html', '#rpid-form'), ('walltime.html', '#walltime-form')]:
            plain.goto((ROOT/'docs'/name).as_uri())
            assert plain.locator('noscript p').first.is_visible(), name
            assert plain.locator(form).is_hidden(), name
            assert plain.evaluate('document.documentElement.scrollWidth <= innerWidth'), name
        plain.goto((ROOT/'docs/agents.html').as_uri())
        assert plain.locator('noscript p').first.is_visible()
        plain.locator('summary').filter(has_text='“Is the HPC working?”').click()
        assert plain.get_by_text('Read-only health check', exact=True).is_visible()
        assert plain.evaluate('document.documentElement.scrollWidth <= innerWidth')
        no_js.close()
        browser.close()
        print('PASS: 8 pages + site nav, home cards, agent selection, RPID validation/privacy, walltime/limits, copy/fallback, print, light/dark preference contrast, desktop/mobile, no-JS and no remote requests')
        print(f'Screenshots: {screenshots}')


if __name__ == '__main__':
    main()
