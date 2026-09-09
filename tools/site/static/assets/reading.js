/* Navigation is rendered in HTML; filtering is an optional enhancement. */
(() => {
  'use strict';
  const panel = document.querySelector('.browse-panel');
  if (!panel) return;
  const mobile = window.matchMedia('(max-width: 900px)');
  const sidebar = document.querySelector('.reading-sidebar');
  const marker = document.createComment('sidebar');
  sidebar.before(marker);
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'browse-toggle';
  button.textContent = 'Browse articles';
  button.setAttribute('aria-controls', 'writing-drawer');
  button.setAttribute('aria-expanded', 'false');
  marker.before(button);
  const drawer = document.createElement('dialog');
  drawer.id = 'writing-drawer';
  drawer.className = 'writing-drawer';
  drawer.setAttribute('aria-label', 'Browse articles');
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'drawer-close';
  close.textContent = 'Close articles ×';
  drawer.append(close);
  document.body.append(drawer);
  function closeDrawer() { drawer.close(); }
  drawer.addEventListener('close', () => {
    document.documentElement.classList.remove('drawer-open');
    button.setAttribute('aria-expanded', 'false');
    if (mobile.matches) button.focus({preventScroll:true});
  });
  close.addEventListener('click', closeDrawer);
  drawer.addEventListener('click', event => {
    if (event.target.closest('a')) closeDrawer();
    if (event.target === drawer) {
      const box = drawer.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closeDrawer();
    }
  });
  button.addEventListener('click', () => {
    panel.open = true;
    drawer.showModal();
    document.documentElement.classList.add('drawer-open');
    button.setAttribute('aria-expanded', 'true');
    close.focus();
  });
  const syncPanel = () => {
    if (drawer.open) closeDrawer();
    panel.open = true;
    button.hidden = !mobile.matches;
    if (mobile.matches) drawer.append(sidebar);
    else marker.after(sidebar);
  };
  syncPanel();
  mobile.addEventListener('change', syncPanel);
  const search = document.querySelector('.navigation-search');
  const input = document.querySelector('#nav-search');
  const status = document.querySelector('.search-status');
  const groups = [...document.querySelectorAll('.topic-group')];
  const initialOpen = new Map(groups.map(group => [group, group.open]));
  search.hidden = false;
  const normalise = text => text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function filter() {
    const terms = normalise(input.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    for (const group of groups) {
      let visible = 0;
      const category = group.querySelector('summary').textContent;
      for (const row of group.querySelectorAll('li')) {
        const text = normalise(category + ' ' + row.textContent);
        row.hidden = !terms.every(term => text.includes(term));
        if (!row.hidden) visible++;
      }
      group.hidden = visible === 0;
      group.open = terms.length ? visible > 0 : initialOpen.get(group);
      count += visible;
    }
    status.textContent = terms.length ? (count ? `${count} article${count === 1 ? '' : 's'} found` : 'No matches. Try another title or topic.') : '';
  }
  input.addEventListener('input', filter);
  input.addEventListener('keydown', event => {
    if (event.key === 'Escape') { input.value = ''; filter(); }
  });
})();
