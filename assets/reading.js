/* Navigation is rendered in HTML; filtering is an optional enhancement. */
(() => {
  'use strict';
  const panel = document.querySelector('.browse-panel');
  if (!panel) return;
  const mobile = window.matchMedia('(max-width: 900px)');
  const syncPanel = () => { panel.open = !mobile.matches; };
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
