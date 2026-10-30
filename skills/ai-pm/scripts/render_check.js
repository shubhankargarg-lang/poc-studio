// Render check, copied verbatim from the design-system skill (v10, Step 6). Evaluates to a result object.
// Keep in sync with that skill: if it changes there, copy it here.
(() => {
  const res = { hScroll: 0, spills: 0, clipped: 0, vclipped: 0, overlaps: 0, squeezed: 0, brokenImages: 0, fonts: {}, unstyledClasses: [], where: [] };
  const note = (k, el, doc, win = window) => { res[k]++; if (res.where.length < 15) res.where.push(k + ': ' + (win.frameElement ? (win.frameElement.title || 'device') : 'page') + ' › ' + el.tagName.toLowerCase() + '.' + [...el.classList].join('.') + ' "' + (el.textContent || '').trim().slice(0, 40) + '"'); };
  const scan = (doc, win) => {
    const de = doc.documentElement; res.hScroll = Math.max(res.hScroll, de.scrollWidth - de.clientWidth);
    const texts = [];
    const layer = el => { for (let n = el; n && n !== doc.body; n = n.parentElement) { const p = win.getComputedStyle(n).position; if (p === 'fixed' || p === 'absolute' || p === 'sticky') return n; } return doc.body; };
    for (const el of doc.querySelectorAll('body *')) {
      const cs = win.getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
      if (['hidden', 'clip'].includes(cs.overflowX) && el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 40 && cs.textOverflow !== 'ellipsis' && !el.closest('.tblwrap')) note('clipped', el, doc, win);
      if (['hidden', 'clip'].includes(cs.overflowY) && el.clientHeight > 0 && el.scrollHeight > el.clientHeight + 2 && cs.webkitLineClamp === 'none' && !el.closest('.frame, .frame-scroll') && [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim())) note('vclipped', el, doc, win);
      const p = el.parentElement;
      if (p && cs.position !== 'fixed' && cs.position !== 'absolute' && win.getComputedStyle(p).overflowX === 'visible' && r.right > p.getBoundingClientRect().right + 4) note('spills', el, doc, win);
      const own = [...el.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim());
      if (own) {
        if (cs.display !== 'inline' && cs.display !== 'contents') texts.push([el, r, layer(el)]);
        const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3, lines = Math.round(r.height / lh), words = el.textContent.trim().split(/\s+/).length;
        if (lines >= 3 && words / lines <= 1.6 && words >= 3) note('squeezed', el, doc, win);
      }
    }
    for (const parent of doc.querySelectorAll('body *')) {
      if (parent.matches('.faces')) continue;
      const kids = [...parent.children].filter(k => { const cs = win.getComputedStyle(k); return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.position !== 'absolute' && cs.position !== 'fixed' && k.textContent.trim(); });
      for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
        const ra = kids[i].getBoundingClientRect(), rb = kids[j].getBoundingClientRect();
        const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
        if (ra.width && rb.width && ix > 3 && iy > 3) note('overlaps', kids[j], doc, win);
      }
    }
    res.brokenImages += [...doc.images].filter(i => i.complete && !i.naturalWidth).length;
    const c = doc.createElement('canvas').getContext('2d');
    doc.fonts.forEach(f => { const fam = f.family.replace(/["']/g, ''); c.font = `16px "${fam}"`; res.fonts[fam] = { status: f.status, spaceEm: +((c.measureText('a b').width - c.measureText('ab').width) / 16).toFixed(2) }; });
    const css = [...doc.styleSheets].flatMap(s => { try { return [...s.cssRules].map(r => r.cssText) } catch (e) { return [] } }).join(' ');
    [...new Set([...doc.querySelectorAll('[class]')].flatMap(e => [...e.classList]))].filter(k => !css.includes('.' + k) && !res.unstyledClasses.includes(k)).forEach(k => res.unstyledClasses.push(k));
  };
  scan(document, window);
  for (const f of document.querySelectorAll('iframe')) { try { if (f.contentDocument) scan(f.contentDocument, f.contentWindow); } catch (e) {} }
  console.table(res); return res;
})()
