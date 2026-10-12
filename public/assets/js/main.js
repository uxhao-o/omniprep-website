/* OmniPrep — shared site interactions */
(function () {
  'use strict';

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
    });
    // Close when a link is clicked
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') nav.classList.remove('open');
    });
  }

  // Back-to-top button
  var toTop = document.querySelector('.to-top');
  if (toTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 600) toTop.classList.add('show');
      else toTop.classList.remove('show');
    }, { passive: true });
    toTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Copy-to-clipboard buttons
  document.querySelectorAll('.copy-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.closest('.code-block').querySelector('pre');
      if (!pre) return;
      var text = pre.innerText;
      var done = function () {
        var old = btn.textContent;
        btn.textContent = 'Copied ✓';
        setTimeout(function () { btn.textContent = old; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done).catch(function () { fallbackCopy(text, done); });
      } else {
        fallbackCopy(text, done);
      }
    });
  });

  function fallbackCopy(text, done) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    done();
  }

  // Active TOC link highlighting (scroll-spy)
  var tocLinks = document.querySelectorAll('.toc a[href^="#"]');
  if (tocLinks.length) {
    var sections = [];
    tocLinks.forEach(function (a) {
      var el = document.querySelector(a.getAttribute('href'));
      if (el) sections.push({ link: a, el: el });
    });
    var onScroll = function () {
      var pos = window.scrollY + 110;
      var current = sections[0];
      sections.forEach(function (s) {
        if (s.el.offsetTop <= pos) current = s;
      });
      tocLinks.forEach(function (a) { a.style.background = ''; a.style.color = ''; });
      if (current) {
        current.link.style.background = 'var(--blue-soft)';
        current.link.style.color = 'var(--blue)';
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();

// Theme toggle (light / dark)
(function () {
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var root = document.documentElement;
    var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next;
    localStorage.setItem('op-theme', next);
  });
})();

// Language toggle: preserve reading position across the language switch.
// Strategy: remember the id of the section currently in view (anchors match
// between EN and ZH pages). On the target page, jump back to that section;
// fall back to the raw scroll offset when no anchor exists.
(function () {
  var KEY = 'op-lang-pos';

  function currentAnchorId() {
    var nodes = document.querySelectorAll('main [id]');
    var pos = window.scrollY + 120;
    var found = null;
    nodes.forEach(function (el) {
      if (el.offsetTop <= pos) found = el.id;
    });
    return found;
  }

  // Capture position right before navigating away.
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.lang-btn');
    if (!btn) return;
    try {
      sessionStorage.setItem(KEY, JSON.stringify({
        hash: currentAnchorId(),
        y: window.scrollY
      }));
    } catch (err) { /* storage unavailable */ }
  });

  // Restore position after the language switch.
  try {
    var saved = sessionStorage.getItem(KEY);
    if (saved) {
      sessionStorage.removeItem(KEY);
      var p = JSON.parse(saved);
      var target = null;
      if (p.hash) target = document.getElementById(p.hash);
      if (target) {
        // Defer so layout (fonts, images) settles; header offset ~ 110px.
        requestAnimationFrame(function () {
          var top = target.getBoundingClientRect().top + window.scrollY - 110;
          window.scrollTo(0, Math.max(0, top));
        });
      } else if (!location.hash && p.y > 0) {
        requestAnimationFrame(function () { window.scrollTo(0, p.y); });
      }
    }
  } catch (err) { /* ignore */ }
})();

// TOC hierarchy: group sub-items under their level-1 parent + collapsible carets.
(function () {
  document.querySelectorAll('.toc > ul').forEach(function (ul) {
    if (ul.dataset.grouped) return;
    ul.dataset.grouped = '1';
    var groups = [];
    var cur = null;
    Array.prototype.forEach.call(ul.children, function (li) {
      var a = li.querySelector('a');
      if (a && a.classList.contains('level-1')) {
        cur = { li: li, sub: [] };
        groups.push(cur);
      } else if (cur) {
        cur.sub.push(li);
      } else {
        groups.push({ li: li, sub: null });
      }
    });
    ul.innerHTML = '';
    groups.forEach(function (g) {
      if (g.sub && g.sub.length) {
        g.li.classList.add('has-sub');
        var row = document.createElement('div');
        row.className = 'toc-row';
        var a = g.li.querySelector('a');
        row.appendChild(a);
        var caret = document.createElement('button');
        caret.type = 'button';
        caret.className = 'toc-caret';
        caret.setAttribute('aria-label', 'Toggle section');
        caret.innerHTML =
          '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
        row.appendChild(caret);
        var sub = document.createElement('ul');
        sub.className = 'toc-sub';
        g.sub.forEach(function (s) { sub.appendChild(s); });
        g.li.innerHTML = '';
        g.li.appendChild(row);
        g.li.appendChild(sub);
        caret.addEventListener('click', function () {
          g.li.classList.toggle('collapsed');
        });
      }
      ul.appendChild(g.li);
    });
  });
})();

// Upgrade bare <pre><code> blocks (markdown-converted pages) into the
// styled .code-block component with header label + copy button.
(function () {
  document.querySelectorAll('article pre').forEach(function (pre) {
    if (pre.closest('.code-block')) return;
    var code = pre.querySelector('code');
    var lang = 'text';
    if (code) {
      var m = (code.className || '').match(/language-([\w-]+)/);
      if (m) lang = m[1];
    }
    var wrap = document.createElement('div');
    wrap.className = 'code-block';
    var head = document.createElement('div');
    head.className = 'cb-head';
    var label = document.createElement('span');
    label.className = 'cb-label';
    label.textContent = lang;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-btn';
    btn.textContent = '复制';
    head.appendChild(label);
    head.appendChild(btn);
    btn.addEventListener('click', function () {
      var done = function () {
        var old = btn.textContent;
        btn.textContent = 'Copied ✓';
        setTimeout(function () { btn.textContent = old; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(pre.innerText).then(done);
      } else {
        var ta = document.createElement('textarea');
        ta.value = pre.innerText;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        done();
      }
    });
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(head);
    wrap.appendChild(pre);
  });
})();
