(function(){
  var KEYS=['data-theme','data-chrome','data-surface','data-density','data-style-set'];
  var SIZES={phone:[390,800],tablet:[820,1000],desktop:[1280,800],wide:[1440,900]};
  var head=[].map.call(document.querySelectorAll('style,link[rel="stylesheet"]'),function(n){return n.outerHTML}).join('');
  function rootAttrs(){var h=document.documentElement;return KEYS.filter(function(a){return h.hasAttribute(a)}).map(function(a){return a+'="'+h.getAttribute(a)+'"'}).join(' ')}
  var items=[];
  [].forEach.call(document.querySelectorAll('template.device'),function(t){
    var kind=t.getAttribute('data-device')||'desktop', sz=SIZES[kind]||SIZES.desktop;
    var W=+(t.getAttribute('data-width')||sz[0]), hAttr=t.getAttribute('data-height')||((kind==='phone'||kind==='tablet')?String(sz[1]):'auto');
    var wrap=document.createElement('div'); wrap.className='device-wrap '+kind;
    if(kind==='phone'||kind==='tablet'){wrap.style.maxWidth=W+'px';wrap.style.borderRadius='var(--r-shell)'}
    var f=document.createElement('iframe'); f.title=t.getAttribute('data-title')||(kind+' specimen');
    f.style.width=W+'px'; f.style.height=(hAttr==='auto'?sz[1]:+hAttr)+'px';
    f.srcdoc='<!doctype html><html '+rootAttrs()+'><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+head+'</head><body>'+t.innerHTML+'</body></html>';
    wrap.appendChild(f); t.parentNode.insertBefore(wrap,t.nextSibling);
    var it={t:t,wrap:wrap,f:f,W:W,auto:hAttr==='auto'}; items.push(it);
    f.addEventListener('load',function(){sync();fit(it);var d=f.contentDocument;if(d&&d.fonts)d.fonts.ready.then(function(){fit(it)});setTimeout(function(){fit(it)},400)});
  });
  function fit(it){
    var d=it.f.contentDocument;
    if(it.auto&&d&&d.documentElement){it.f.style.height='0px';var h=Math.min(Math.max(d.documentElement.scrollHeight,480),2600);it.f.style.height=h+'px'}
    var s=Math.min(1,it.wrap.clientWidth/it.W);
    it.f.style.transform='scale('+s+')';
    it.wrap.style.height=(parseFloat(it.f.style.height)*s)+'px';
  }
  function sync(){var h=document.documentElement;items.forEach(function(it){var d=it.f.contentDocument;if(!d||!d.documentElement)return;KEYS.forEach(function(a){if(h.hasAttribute(a))d.documentElement.setAttribute(a,h.getAttribute(a));else d.documentElement.removeAttribute(a)})})}
  new MutationObserver(function(){sync();items.forEach(fit)}).observe(document.documentElement,{attributes:true,attributeFilter:KEYS});
  if(window.ResizeObserver){var ro=new ResizeObserver(function(){items.forEach(fit)});items.forEach(function(it){ro.observe(it.wrap)})}
  else window.addEventListener('resize',function(){items.forEach(fit)});
})();
